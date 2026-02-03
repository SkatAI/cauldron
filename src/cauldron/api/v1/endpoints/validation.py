import logging

from fastapi import APIRouter, Request

from cauldron.api.v1.schemas import (
    ErrorCode,
    ValidateRequest,
    ValidateResponse,
    ValidationError,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/validate", response_model=ValidateResponse)
async def validate(request: Request, body: ValidateRequest) -> ValidateResponse:
    graph = request.app.state.graph

    try:
        result = await graph.ainvoke({"content": body.content})
    except Exception:
        logger.exception("Validation graph failed")
        return ValidateResponse(
            status="invalid",
            errors=[
                ValidationError(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="Internal validation error",
                )
            ],
        )

    all_errors: list[ValidationError] = result.get("all_errors", [])

    return ValidateResponse(
        status="invalid" if all_errors else "valid",
        errors=all_errors,
        quality=result.get("quality_evaluation"),
    )
