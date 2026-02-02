import json
import logging
import re

from langchain_openai import ChatOpenAI

from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ErrorCode, ValidationError
from cauldron.llm.prompts import moderation_prompt

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    """Strip markdown fences if present."""
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


async def moderate_content(state: ValidationState, *, llm: ChatOpenAI) -> ValidationState:
    """Use LLM to detect toxic or NSFW content."""
    content = state["content"]
    errors: list[ValidationError] = []

    try:
        chain = moderation_prompt | llm
        response = await chain.ainvoke({"content": content})
        raw = str(response.content)
        logger.debug("Moderation raw response: %s", raw)
        result = json.loads(_extract_json(raw))

        for issue in result.get("issues", []):
            issue_type = issue.get("type", "toxic_content")
            if issue_type == "nsfw_content":
                code = ErrorCode.NSFW_CONTENT
            else:
                code = ErrorCode.TOXIC_CONTENT

            errors.append(
                ValidationError(
                    code=code,
                    message=f"Content contains {issue_type.replace('_', ' ')}",
                    detail=issue.get("description"),
                )
            )
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse moderation response: %s — raw: %s", exc, raw)
        errors.append(
            ValidationError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Failed to parse moderation response",
            )
        )
    except Exception as exc:
        logger.error("Moderation check failed: %s", exc, exc_info=True)
        errors.append(
            ValidationError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Moderation check failed",
            )
        )

    return ValidationState(moderation_errors=errors)
