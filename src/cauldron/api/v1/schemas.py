from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ValidateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Markdown content to validate")


class ErrorCode(str, Enum):
    MISSING_SECTION = "missing_section"
    TOXIC_CONTENT = "toxic_content"
    NSFW_CONTENT = "nsfw_content"
    PARSE_ERROR = "parse_error"
    INTERNAL_ERROR = "internal_error"


class ValidationError(BaseModel):
    code: ErrorCode
    message: str
    detail: str | None = None


class ValidateResponse(BaseModel):
    status: Literal["valid", "invalid"]
    errors: list[ValidationError] = Field(default_factory=list)
