# Development Guide

Quick-start for local development. For the full contributor workflow (PRs, code style, changelog, releases) see [docs/contributing.md](docs/contributing.md); for test patterns see [docs/testing.md](docs/testing.md); for how the app is structured see [docs/architecture.md](docs/architecture.md).

## Quick Start

```bash
git clone https://github.com/reuteras/miniflux-tui-py.git
cd miniflux-tui-py
uv sync --all-groups        # install all deps, including dev/docs
uv run pre-commit install   # install pre-commit hooks
```

```bash
uv run pytest tests                     # run tests
uv run ruff check miniflux_tui tests    # lint
uv run ruff format miniflux_tui tests   # format
uv run pyright miniflux_tui tests       # type check
uv run miniflux-tui --init              # initialize config
uv run miniflux-tui                     # run the app
uv run zensical serve                   # preview docs at localhost:8000
```

## Git Workflow

Direct commits to `main` are allowed; feature branches are optional but fine for larger changes. See [AGENT.md](AGENT.md) for the full commit/CI conventions used in this repo.

## Debugging

```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

## Performance

- Avoid blocking operations in async code; use `run_in_executor` for sync calls from async context.
- Cache API responses when appropriate.
- Profile with the tools in `miniflux_tui/performance.py`.

## Dependency Updates

Managed by Renovate: security patches land immediately, regular updates batch on Mondays, major-version updates batch on Sundays and need manual approval. See the Dependency Dashboard issue for pending updates.

## Troubleshooting

| Problem | Fix |
|---|---|
| Pre-commit hooks not running | `uv run pre-commit install` |
| Outdated dependencies | `uv sync --all-groups --upgrade` |
| `.venv` / interpreter issues | `uv sync --all-groups` (recreates it) |
| Tests failing | `uv run pytest tests -vv` for detail |
| Type errors | `uv run pyright` |

## Getting Help

GitHub Discussions for questions, GitHub Issues for bugs, [SECURITY.md](SECURITY.md) for security issues.
