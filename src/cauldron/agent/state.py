from typing import TypedDict

from cauldron.api.v1.schemas import ValidationError


class ValidationState(TypedDict, total=False):
    content: str
    section_errors: list[ValidationError]
    moderation_errors: list[ValidationError]
    all_errors: list[ValidationError]
