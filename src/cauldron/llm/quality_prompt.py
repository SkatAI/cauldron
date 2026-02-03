from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

_EVALUATOR_PROMPT_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "docs"
    / "prompts"
    / "system_prompt_quality_evaluator_fr.md"
)

QUALITY_SYSTEM = """\
{evaluator_instructions}

Réponds UNIQUEMENT avec un objet JSON (sans balises markdown) avec cette structure exacte :
{{{{
  "criteria": [
    {{{{"name": "Clarté du rôle", "score": 1-5, "justification": "..."}}}},
    {{{{"name": "Traits de comportement et attitude", "score": 1-5, "justification": "..."}}}},
    {{{{"name": "Style de communication", "score": 1-5, "justification": "..."}}}},
    {{{{"name": "Motivations et objectifs", "score": 1-5, "justification": "..."}}}},
    {{{{"name": "Contraintes et limitations", "score": 1-5, "justification": "..."}}}},
    {{{{"name": "Instructions de cohérence", "score": 1-5, "justification": "..."}}}},
    {{{{"name": "Pertinence contextuelle", "score": 1-5, "justification": "..."}}}},
    {{{{"name": "Clarté et concision", "score": 1-5, "justification": "..."}}}}
  ],
  "overall_score": 1-5,
  "advice": "Suggestions d'amélioration concrètes en français..."
}}}}
"""

QUALITY_HUMAN = "Évalue ce system prompt définissant un persona :\n\n{content}"


def _load_evaluator_instructions() -> str:
    return _EVALUATOR_PROMPT_PATH.read_text(encoding="utf-8")


def get_quality_prompt() -> ChatPromptTemplate:
    evaluator_instructions = _load_evaluator_instructions()
    system_message = QUALITY_SYSTEM.format(evaluator_instructions=evaluator_instructions)
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", QUALITY_HUMAN),
        ]
    )


quality_prompt = get_quality_prompt()
