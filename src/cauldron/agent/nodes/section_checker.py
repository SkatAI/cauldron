import re

from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ErrorCode, ValidationError
from cauldron.config.sections import SectionsConfig


def check_sections(state: ValidationState, *, config: SectionsConfig) -> ValidationState:
    """Check that all required sections are present in the markdown content."""
    content = state["content"]
    errors: list[ValidationError] = []

    for section in config.sections:
        if not section.required:
            continue
        pattern = re.compile(section.heading_pattern, re.MULTILINE)
        if not pattern.search(content):
            errors.append(
                ValidationError(
                    code=ErrorCode.MISSING_SECTION,
                    message=f"La section requise « {section.name} » est manquante",
                    detail=f"En-tête attendu correspondant au motif : {section.heading_pattern}",
                )
            )

    return ValidationState(section_errors=errors)
