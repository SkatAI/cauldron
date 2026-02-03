from typing import Any

from fastapi import APIRouter

root_router = APIRouter()


@root_router.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok"}
