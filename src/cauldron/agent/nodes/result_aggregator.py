from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ValidationError


def aggregate_results(state: ValidationState) -> ValidationState:
    """Collect moderation_errors into all_errors. Pass through quality_evaluation."""
    moderation_errors: list[ValidationError] = state.get("moderation_errors", [])
    return ValidationState(all_errors=moderation_errors)
