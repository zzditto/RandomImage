# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RandomImage is a FastAPI-based random image service with smart compression. It serves random images from configured directories with on-the-fly resizing, format conversion, and quality optimization. All documentation, comments, and logs are in Chinese (Simplified).

## Development Commands

```bash
# Install dependencies (requires uv package manager)
uv sync

# Run in development mode (auto-loads .env via python-dotenv)
uv run python -m src.random_image.main

# Run production server
uv run uvicorn src.random_image.main:app --host 0.0.0.0 --port 8000

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_api.py

# Run tests with coverage
uv run pytest --cov=src/random_image

# Code formatting
uv run black src/ tests/

# Linting
uv run ruff check src/ tests/
```

## Architecture

Layered FastAPI application under `src/random_image/`:

- **API layer** (`api/routes.py`, `api/dependencies.py`) — Endpoint definitions and request parameter validation via FastAPI dependency injection. Routes mounted at `/api/v1`.
- **Service layer** (`services/image_service.py`) — Business logic: image scanning, random selection, processing orchestration, LRU caching, statistics.
- **Utility layer** (`utils/image_processor.py`) — Low-level Pillow operations (resize, format conversion, compression). Includes `calculate_optimal_quality()` which tier-sizes quality based on source file size.
- **Config** (`config.py`) — `Settings` class reads config from environment variables. Uses `python-dotenv` to auto-load `.env` for local dev; Docker `-e` vars take priority. Validated at startup via `validate_config()`.
- **Models** (`models.py`) — Pure dataclasses and enums (no framework coupling).
- **Exceptions** (`exceptions.py`) — Custom exception hierarchy with HTTP status mapping in `EXCEPTION_HANDLERS`.
- **Entry point** (`main.py`) — Factory function `create_app()` wires middleware, routes, and exception handlers. Lifespan handler validates config and initializes services.

Singleton instances at module level: `settings`, `image_service`, `image_processor`.

## Key Patterns

- **App factory**: `create_app()` in `main.py` — all wiring happens here.
- **LRU cache**: `ImageCache` in `image_service.py` uses `collections.OrderedDict`, keyed by MD5(path + params).
- **Dependency injection**: `api/dependencies.py` provides `get_image_params()` for parsing query parameters.
- **Conventional commits**: Uses Chinese-language conventional commits (`chore(git):`, `docs:`, `style(...):`).

## Code Standards

- Python 3.11+ (pinned in `.python-version` and tool configs)
- Line length: 88 (black and ruff)
- Ruff rules: E, W, F, I, C, B (pycodestyle, pyflakes, isort, mccabe, flake8-bugbear)
- Async tests use `asyncio_mode = "auto"` (no need for `@pytest.mark.asyncio` decorators)

## Environment Variables

Config via environment variables (`.env` for local dev, `-e` flags for Docker). Key variables: `IMAGE_DIR` (source directory), `COMPRESSION_QUALITY` (60-95), `OUTPUT_FORMAT` (WEBP/JPEG/PNG), `ENABLE_CACHE`, `CACHE_MAX_SIZE`, `MAX_IMAGE_SIZE`, `DEFAULT_WIDTH`. See `.env.example` for full list.
