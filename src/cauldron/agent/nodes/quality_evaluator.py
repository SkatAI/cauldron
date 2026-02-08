import json
import logging
import re

from langchain_openai import ChatOpenAI

from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import QualityCriterion, QualityEvaluation
from cauldron.llm.quality_prompt import quality_prompt

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    """Strip markdown fences if present."""
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


async def evaluate_quality(state: ValidationState, *, llm: ChatOpenAI) -> ValidationState:
    """Use LLM to evaluate the quality of a persona system prompt."""
    content = state["content"]

    try:
        chain = quality_prompt | llm
        response = await chain.ainvoke({"content": content})
        raw = str(response.content)
        logger.info("Quality agent response: %s", raw)
        logger.debug("Quality evaluation raw response: %s", raw)
        result = json.loads(_extract_json(raw))

        criteria = [
            QualityCriterion(
                name=c["name"],
                justification=c["justification"],
            )
            for c in result.get("criteria", [])
        ]

        advice = result.get("advice", "")
        if isinstance(advice, list):
            advice = "\n".join(str(item) for item in advice)
        elif advice is None:
            advice = ""

        quality_evaluation = QualityEvaluation(
            criteria=criteria,
            advice=str(advice),
        )

        return ValidationState(quality_evaluation=quality_evaluation)

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse quality evaluation response: %s — raw: %s", exc, raw)
        return ValidationState(quality_evaluation=None)
    except Exception as exc:
        logger.error("Quality evaluation failed: %s", exc, exc_info=True)
        return ValidationState(quality_evaluation=None)
