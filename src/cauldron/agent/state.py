from typing import TypedDict

from cauldron.api.v1.schemas import QualityEvaluation, ValidationError


class ValidationState(TypedDict, total=False):
    content: str
    quality_evaluation: QualityEvaluation | None
    moderation_errors: list[ValidationError]
    all_errors: list[ValidationError]
