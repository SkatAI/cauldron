# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
make dev              # Install all deps (including dev tools)
make run              # Start dev server on port 8088 with hot-reload
make test             # Run full test suite
make test-unit        # Run unit tests only
make test-cov         # Run tests with coverage report
make lint             # Run ruff linter
make format           # Auto-format with ruff
make type-check       # Run mypy (strict mode)
make docker-up        # Start containers (port 8088)
make docker-down      # Stop containers
```

Run a single test file or test function:
```bash
uv run pytest tests/unit/agent/test_section_checker.py
uv run pytest tests/unit/agent/test_section_checker.py::test_missing_sections
```

## Architecture

Cauldron is a FastAPI service that validates AI persona system prompts (markdown) using a LangGraph workflow. LLM calls go through OpenRouter.

### Request Flow

```
POST /v1/validate → validation.py endpoint → app.state.graph.ainvoke({"content": ...})
```

The graph is compiled once at startup in `main.py` lifespan and stored in `app.state.graph`.

### LangGraph Pipeline

```
START → check_sections → (conditional) → moderate_content → aggregate_results → END
                              └─ empty content ──────────→ aggregate_results → END
```

- **check_sections** (`agent/nodes/section_checker.py`): Pure Python. Regex matches markdown headings against patterns from `config/required_sections.yaml`.
- **moderate_content** (`agent/nodes/content_moderator.py`): Async. Sends content to LLM via `moderation_prompt | llm` chain, parses JSON response for toxic/NSFW issues.
- **aggregate_results** (`agent/nodes/result_aggregator.py`): Merges `section_errors` + `moderation_errors` into `all_errors`.

State is `ValidationState` (TypedDict) with keys: `content`, `section_errors`, `moderation_errors`, `all_errors`.

### LLM Integration

`ChatOpenRouter` (`llm/client.py`) extends `ChatOpenAI` with OpenRouter defaults. The moderation prompt (`llm/prompts.py`) asks the LLM to return structured JSON with `is_toxic`, `is_nsfw`, and `issues[]`.

### Configuration

- **Secrets/env**: `.env.local` loaded by pydantic-settings (`settings.py`). No `export` prefixes.
- **Business config**: `config/required_sections.yaml` — each section has `name`, `heading_pattern` (regex), `required` (bool).

## Testing Patterns

Tests use pytest with `asyncio_mode = "auto"`. Key fixtures are in `tests/conftest.py`.

**Mocking the LLM chain** in content moderator tests: patch `moderation_prompt` with a mock that overrides `__or__` to return an `AsyncMock` chain:

```python
mock_prompt = MagicMock()
mock_chain = AsyncMock()
mock_chain.ainvoke = AsyncMock(return_value=response)
mock_prompt.__or__ = MagicMock(return_value=mock_chain)
patch("cauldron.agent.nodes.content_moderator.moderation_prompt", mock_prompt)
```

**Integration tests** use `TestClient` with a mocked graph (`AsyncMock`) set on `app.state.graph`.

## Code Style

- Python 3.12, src-layout (`src/cauldron/`)
- Ruff: line-length 100, select rules E, F, I, N, W, UP
- Mypy strict (with `ignore_missing_imports` for langchain/langgraph modules)
- snake_case for functions/variables, PascalCase for classes
