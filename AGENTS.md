# Repository Guidelines

## Project Structure & Module Organization
- `src/cauldron/` contains the FastAPI app, settings, API routes, and the LangGraph validation pipeline.
- `src/cauldron/agent/` holds graph state, nodes, and orchestration logic; node implementations live in `src/cauldron/agent/nodes/`.
- `config/` stores runtime configuration such as `config/required_sections.yaml`.
- `tests/unit/` and `tests/integration/` contain unit and integration tests respectively.
- `docs/` holds supporting documentation; `Dockerfile` and `docker-compose.yaml` define container workflows.

## Build, Test, and Development Commands
- `make dev`: install all dependencies (including dev tools) via `uv`.
- `make run`: start the API on port 8088 with hot reload.
- `make test`: run the full test suite; `make test-unit` and `make test-integration` scope runs.
- `make test-cov`: run tests with coverage reports (`htmlcov/`).
- `make lint` / `make format`: run Ruff checks and auto-formatting.
- `make type-check`: run strict mypy type checks.
- `make docker-up` / `make docker-down`: manage containers for local Docker workflows.

## Coding Style & Naming Conventions
- Python 3.12; keep code in `src/` and tests in `tests/`.
- Ruff is the formatter and linter (line length 100). Prefer `snake_case` for functions and variables; `PascalCase` for classes.
- Mypy runs in strict mode; add types for new public functions and complex data structures.

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio` (auto mode).
- Place unit tests in `tests/unit/` and integration tests in `tests/integration/` (mark with `@pytest.mark.integration`).
- Name tests `test_<behavior>.py` and `test_<behavior>_<case>()` for clarity.

## Commit & Pull Request Guidelines
- Commit messages in history are short, imperative sentences (e.g., “Fix env loading”). Follow that style.
- PRs should include a concise summary, testing evidence (commands + results), and any config changes.
- If behavior changes, update or add tests and note any API changes in the description.

## Configuration & Secrets
- Use `.env.local` for local settings; do not commit secrets.
- Required sections live in `config/required_sections.yaml`. Update this file when changing validation requirements.
