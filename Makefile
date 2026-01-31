.PHONY: install dev test test-unit test-integration test-cov lint format type-check run docker-build docker-up docker-down clean

install:
	uv sync

dev:
	uv sync --all-extras

test:
	uv run pytest

test-unit:
	uv run pytest tests/unit

test-integration:
	uv run pytest tests/integration -m integration

test-cov:
	uv run pytest --cov=cauldron --cov-report=html --cov-report=term

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

type-check:
	uv run mypy src

run:
	uv run uvicorn cauldron.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf .venv __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
