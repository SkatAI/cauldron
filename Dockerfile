# syntax=docker/dockerfile:1

# --- Build stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY src/ src/

RUN uv sync --no-dev

# --- Runtime stage ---
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ src/
COPY docs/ docs/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8088

CMD ["uvicorn", "cauldron.main:app", "--host", "0.0.0.0", "--port", "8088"]
