import logging
import secrets
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from cauldron.agent.graph import compile_graph
from cauldron.api.router import root_router
from cauldron.api.v1.router import v1_router
from cauldron.llm.client import get_llm
from cauldron.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("Starting Cauldron with model=%s", settings.openrouter_model)
    llm = get_llm()
    app.state.graph = compile_graph(llm)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Cauldron", version="0.1.0", lifespan=lifespan)

    @app.middleware("http")
    async def require_bff_secret(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        expected_secret = settings.bff_shared_secret.strip()
        path = request.url.path
        is_public_path = (
            path == "/health"
            or path == "/openapi.json"
            or path.startswith("/docs")
            or path.startswith("/redoc")
        )

        if expected_secret and not is_public_path:
            provided_secret = request.headers.get("X-BFF-Secret", "")
            if not secrets.compare_digest(provided_secret, expected_secret):
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)

    app.include_router(root_router)
    app.include_router(v1_router, prefix="/v1")
    return app


app = create_app()
