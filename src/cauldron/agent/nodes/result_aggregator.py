from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ValidationError


def aggregate_results(state: ValidationState) -> ValidationState:
    """Merge section_errors and moderation_errors into all_errors."""
    section_errors: list[ValidationError] = state.get("section_errors", [])
    moderation_errors: list[ValidationError] = state.get("moderation_errors", [])
    return ValidationState(all_errors=[*section_errors, *moderation_errors])
