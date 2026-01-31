import json
import logging

from langchain_openai import ChatOpenAI

from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ErrorCode, ValidationError
from cauldron.llm.prompts import moderation_prompt

logger = logging.getLogger(__name__)


async def moderate_content(state: ValidationState, *, llm: ChatOpenAI) -> ValidationState:
    """Use LLM to detect toxic or NSFW content."""
    content = state["content"]
    errors: list[ValidationError] = []

    try:
        chain = moderation_prompt | llm
        response = await chain.ainvoke({"content": content})
        result = json.loads(str(response.content))

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
    except json.JSONDecodeError:
        logger.exception("Failed to parse moderation response")
        errors.append(
            ValidationError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Failed to parse moderation response",
            )
        )
    except Exception:
        logger.exception("Moderation check failed")
        errors.append(
            ValidationError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Moderation check failed",
            )
        )

    return ValidationState(moderation_errors=errors)
