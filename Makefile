.DEFAULT_GOAL := help

.PHONY: help install dev test test-unit test-integration test-cov lint format type-check run docker-build docker-up docker-logs docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync

dev: ## Install all dependencies including dev tools
	uv sync --all-extras

test: ## Run all tests
	uv run pytest

test-unit: ## Run unit tests only
	uv run pytest tests/unit

test-integration: ## Run integration tests only
	uv run pytest tests/integration -m integration

test-cov: ## Run tests with coverage report
	uv run pytest --cov=cauldron --cov-report=html --cov-report=term

lint: ## Run ruff linter
	uv run ruff check src tests

format: ## Auto-format code with ruff
	uv run ruff format src tests

type-check: ## Run mypy type checker
	uv run mypy src

run: ## Start dev server on port 8088 with hot-reload
	uv run uvicorn cauldron.main:app --reload --host 0.0.0.0 --port 8088

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start containers in background
	docker compose up -d

docker-logs: ## Tail container logs
	docker compose logs -f

docker-down: ## Stop containers
	docker compose down

clean: ## Remove build artifacts and caches
	rm -rf .venv __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
