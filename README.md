# Cauldron

AI agent service that validates AI persona system prompts. Built with FastAPI, LangGraph, and LangChain, using LLMs via OpenRouter.

## What it does

Receives markdown-formatted system prompts and:
- **Quality evaluation** — LLM-based assessment of persona quality across 8 criteria (role clarity, behavior traits, communication style, etc.) with scores and improvement advice in French
- **Content moderation** — detects toxic and NSFW content via LLM (blocking validation)

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- An [OpenRouter](https://openrouter.ai/) API key

## Setup

```bash
# Install dependencies
make dev

# Copy and fill in your environment variables
cp .env.example .env.local
# Edit .env.local and set OPENROUTER_API_KEY
```

## Usage

### Run the server

```bash
make run
```

The API starts on `http://localhost:8088`.

### API endpoints

**Health check**

```bash
curl http://localhost:8088/health
# {"status": "ok"}
```

**Validate a system prompt**

```bash
curl -X POST http://localhost:8088/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Personality\nFriendly assistant.\n\n## Tone\nProfessional.\n\n## Behavior\nAnswer clearly.\n\n## Constraints\nNo medical advice."
  }'
```

Response when valid:
```json
{
  "status": "valid",
  "errors": [],
  "quality": {
    "criteria": [
      {"name": "Clarté du rôle", "score": 4, "justification": "..."},
      {"name": "Traits de comportement et attitude", "score": 3, "justification": "..."},
      ...
    ],
    "overall_score": 4,
    "advice": "Suggestions d'amélioration..."
  }
}
```

Response when invalid (toxic/NSFW content detected):
```json
{
  "status": "invalid",
  "errors": [
    {"code": "toxic_content", "message": "Le contenu contient du contenu toxique", "detail": "..."}
  ],
  "quality": { ... }
}
```

Error codes: `toxic_content`, `nsfw_content`, `parse_error`, `internal_error`.

### Docker

```bash
# Build and start
make docker-up

# Stop
make docker-down
```

The `docker-compose.yaml` mounts `src/` for hot-reload during development.

## Configuration

### Environment variables (`.env.local`)

| Variable | Description | Default |
|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter API key (required) | — |
| `OPENROUTER_MODEL` | Model for moderation and quality evaluation (required) | — |
| `OPENROUTER_BASE_URL` | OpenRouter API base URL | `https://openrouter.ai/api/v1` |
| `LANGSMITH_API_KEY` | LangSmith tracing key (optional) | — |
| `LANGSMITH_PROJECT` | LangSmith project name | `cauldron` |
| `APP_ENV` | Environment name | `development` |
| `LOG_LEVEL` | Logging level | `info` |

## Development

```bash
make dev          # Install all deps including dev tools
make test         # Run all tests
make test-unit    # Run unit tests only
make test-cov     # Run tests with coverage report
make lint         # Run ruff linter
make format       # Auto-format with ruff
make type-check   # Run mypy
make clean        # Remove build artifacts and caches
```

## Project structure

```
src/cauldron/
  main.py              # FastAPI app factory + lifespan
  settings.py          # pydantic-settings (env vars)
  api/                 # HTTP layer
    router.py          # /health
    v1/
      schemas.py       # Request/response models + QualityEvaluation
      endpoints/
        validation.py  # POST /v1/validate
  agent/               # LangGraph workflow
    state.py           # ValidationState TypedDict
    graph.py           # Graph definition + compilation
    nodes/
      quality_evaluator.py    # LLM-based quality assessment
      content_moderator.py    # LLM-based moderation
      result_aggregator.py    # Aggregates moderation errors
  llm/
    client.py          # ChatOpenRouter (extends ChatOpenAI)
    prompts.py         # Moderation prompt template
    quality_prompt.py  # Quality evaluation prompt template
docs/
  system_prompt_quality_evaluator_fr.md  # French evaluator instructions
```
