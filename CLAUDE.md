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
uv run pytest tests/unit/agent/test_quality_evaluator.py
uv run pytest tests/unit/agent/test_quality_evaluator.py::test_quality_evaluation_success
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
START → evaluate_quality → (conditional) → moderate_content → aggregate_results → END
                                └─ empty content ──────────→ aggregate_results → END
```

- **evaluate_quality** (`agent/nodes/quality_evaluator.py`): Async. Sends content to LLM via `quality_prompt | llm` chain, parses JSON response with 8 criteria scores, overall score, and advice.
- **moderate_content** (`agent/nodes/content_moderator.py`): Async. Sends content to LLM via `moderation_prompt | llm` chain, parses JSON response for toxic/NSFW issues.
- **aggregate_results** (`agent/nodes/result_aggregator.py`): Collects `moderation_errors` into `all_errors`.

State is `ValidationState` (TypedDict) with keys: `content`, `quality_evaluation`, `moderation_errors`, `all_errors`.

### LLM Integration

`ChatOpenRouter` (`llm/client.py`) extends `ChatOpenAI` with OpenRouter defaults.

- **Moderation prompt** (`llm/prompts.py`): Returns structured JSON with `is_toxic`, `is_nsfw`, and `issues[]`.
- **Quality prompt** (`llm/quality_prompt.py`): Loads evaluator instructions from `docs/system_prompt_quality_evaluator_fr.md`, returns JSON with 8 criteria scores and improvement advice.

### Configuration

- **Secrets/env**: `.env.local` loaded by pydantic-settings (`settings.py`). No `export` prefixes.

## Testing Patterns

Tests use pytest with `asyncio_mode = "auto"`. Key fixtures are in `tests/conftest.py`.

**Mocking the LLM chain** in moderator/evaluator tests: patch the prompt with a mock that overrides `__or__` to return an `AsyncMock` chain:

```python
mock_prompt = MagicMock()
mock_chain = AsyncMock()
mock_chain.ainvoke = AsyncMock(return_value=response)
mock_prompt.__or__ = MagicMock(return_value=mock_chain)
patch("cauldron.agent.nodes.content_moderator.moderation_prompt", mock_prompt)
# or for quality evaluator:
patch("cauldron.agent.nodes.quality_evaluator.quality_prompt", mock_prompt)
```

**Integration tests** use `TestClient` with a mocked graph (`AsyncMock`) set on `app.state.graph`.

## Code Style

- Python 3.12, src-layout (`src/cauldron/`)
- Ruff: line-length 100, select rules E, F, I, N, W, UP
- Mypy strict (with `ignore_missing_imports` for langchain/langgraph modules)
- snake_case for functions/variables, PascalCase for classes
