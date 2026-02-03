# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Changed

- Switch env file from `.env` to `.env.local` for settings, docker-compose, and docs
- Add `make help` as default target showing all available commands with descriptions
- **Breaking**: Replace blocking section check with non-blocking LLM-based quality evaluation
- Validation now only blocks on toxic/NSFW content; missing sections no longer cause `invalid` status
- API response now includes `quality` field with detailed evaluation scores

### Added

- `.dockerignore` to keep Docker build context minimal
- `QualityEvaluation` and `QualityCriterion` response models
- Quality evaluator node using French evaluator prompt (`docs/system_prompt_quality_evaluator_fr.md`)
- `quality_prompt.py` for LLM-based quality assessment
- Quality evaluation returns 8 criteria scores (1-5), overall score, and improvement advice in French

### Removed

- `MISSING_SECTION` error code (no longer blocking)
- `config/required_sections.yaml` and related section config loading
- `section_checker.py` node (replaced by `quality_evaluator.py`)
- `REQUIRED_SECTIONS_PATH` environment variable

## [0.1.0] - 2025-01-31

### Added

- FastAPI application with app factory pattern and lifespan management
- `POST /v1/validate` endpoint for validating AI persona system prompts
- `GET /health` endpoint
- LangGraph validation pipeline: section checker -> content moderator -> result aggregator
- Section checker node: regex-based validation of required markdown headings
- Content moderator node: LLM-based detection of toxic and NSFW content via OpenRouter
- Result aggregator node: merges section and moderation errors
- Conditional short-circuit in graph: skips moderation when content is empty
- Pydantic-settings configuration with `.env` support
- YAML-based required sections config (`config/required_sections.yaml`)
- `ChatOpenRouter` LLM client extending `ChatOpenAI` for OpenRouter API
- Moderation prompt template
- Request/response schemas with typed error codes (`missing_section`, `toxic_content`, `nsfw_content`, `parse_error`, `internal_error`)
- Multi-stage Dockerfile with uv
- docker-compose.yaml with hot-reload for local development
- Makefile with targets: install, dev, test, test-unit, test-integration, test-cov, lint, format, type-check, run, docker-build, docker-up, docker-down, clean
- Unit tests for section checker, content moderator, graph builder, LLM client, config loader
- Integration tests for validation endpoint
