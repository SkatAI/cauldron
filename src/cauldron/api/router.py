from fastapi import APIRouter

root_router = APIRouter()


@root_router.get("/health")
async def health():
    return {"status": "ok"}
