from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ValidateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Markdown content to validate")


class ErrorCode(str, Enum):
    TOXIC_CONTENT = "toxic_content"
    NSFW_CONTENT = "nsfw_content"
    PARSE_ERROR = "parse_error"
    INTERNAL_ERROR = "internal_error"


class ValidationError(BaseModel):
    code: ErrorCode
    message: str
    detail: str | None = None


class QualityCriterion(BaseModel):
    name: str
    score: int = Field(..., ge=1, le=5)
    justification: str


class QualityEvaluation(BaseModel):
    criteria: list[QualityCriterion]
    overall_score: int = Field(..., ge=1, le=5)
    advice: str


class ValidateResponse(BaseModel):
    status: Literal["valid", "invalid"]
    errors: list[ValidationError] = Field(default_factory=list)
    quality: QualityEvaluation | None = None
