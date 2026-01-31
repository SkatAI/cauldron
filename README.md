# Cauldron

AI agent service that validates AI persona system prompts. Built with FastAPI, LangGraph, and LangChain, using LLMs via OpenRouter.

## What it does

Receives markdown-formatted system prompts and validates them for:
- **Required sections** — configurable headings that must be present (Personality, Tone, Behavior, Constraints by default)
- **Content moderation** — detects toxic and NSFW content via LLM

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

The API starts on `http://localhost:8000`.

### API endpoints

**Health check**

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

**Validate a system prompt**

```bash
curl -X POST http://localhost:8000/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Personality\nFriendly assistant.\n\n## Tone\nProfessional.\n\n## Behavior\nAnswer clearly.\n\n## Constraints\nNo medical advice."
  }'
```

Response when valid:
```json
{"status": "valid", "errors": []}
```

Response when invalid:
```json
{
  "status": "invalid",
  "errors": [
    {"code": "missing_section", "message": "Required section 'Tone' is missing", "detail": "..."}
  ]
}
```

Error codes: `missing_section`, `toxic_content`, `nsfw_content`, `parse_error`, `internal_error`.

### Docker

```bash
# Build and start
make docker-up

# Stop
make docker-down
```

The `docker-compose.yaml` mounts `src/` and `config/` for hot-reload during development.

## Configuration

### Environment variables (`.env`)

| Variable | Description | Default |
|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter API key (required) | — |
| `OPENROUTER_MODEL` | Model for moderation | `meta-llama/llama-3.1-8b-instruct` |
| `OPENROUTER_BASE_URL` | OpenRouter API base URL | `https://openrouter.ai/api/v1` |
| `LANGSMITH_API_KEY` | LangSmith tracing key (optional) | — |
| `LANGSMITH_PROJECT` | LangSmith project name | `cauldron` |
| `APP_ENV` | Environment name | `development` |
| `LOG_LEVEL` | Logging level | `info` |
| `REQUIRED_SECTIONS_PATH` | Path to sections config | `config/required_sections.yaml` |

### Required sections (`config/required_sections.yaml`)

Define which headings must appear in the markdown:

```yaml
sections:
  - name: Personality
    heading_pattern: "^#{1,3}\\s+Personality"
    required: true
```

Each section has a `name`, a `heading_pattern` (regex matched against lines), and a `required` flag.

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
      schemas.py       # Request/response models
      endpoints/
        validation.py  # POST /v1/validate
  agent/               # LangGraph workflow
    state.py           # ValidationState TypedDict
    graph.py           # Graph definition + compilation
    nodes/
      section_checker.py      # Regex-based heading validation
      content_moderator.py    # LLM-based moderation
      result_aggregator.py    # Merges all errors
  llm/
    client.py          # ChatOpenRouter (extends ChatOpenAI)
    prompts.py         # Moderation prompt template
  config/
    loader.py          # YAML config loader
    sections.py        # SectionConfig pydantic model
```
