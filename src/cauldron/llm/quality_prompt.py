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
    {{{{"name": "Clarté du rôle", "justification": "..."}}}},
    {{{{"name": "Traits de comportement et attitude", "justification": "..."}}}},
    {{{{"name": "Style de communication", "justification": "..."}}}},
    {{{{"name": "Motivations et objectifs", "justification": "..."}}}},
    {{{{"name": "Contraintes et limitations", "justification": "..."}}}},
    {{{{"name": "Instructions de cohérence", "justification": "..."}}}},
    {{{{"name": "Pertinence contextuelle", "justification": "..."}}}},
    {{{{"name": "Clarté et concision", "justification": "..."}}}}
  ],
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
