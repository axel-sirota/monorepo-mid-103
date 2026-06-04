---
paths:
  - "apps/user-service/**/*.py"
---

# FastAPI / Python conventions (user-service)

Loaded when Claude reads any Python file under `apps/user-service/`. Engineer persona ships this in 102 lab 1, scoped to user-service only. (A data-scientist student takes 102 separately and ships their OWN `fastapi.md` scoped to `ml/**`.)

## Runtime + deps

- Python 3.12.
- FastAPI 0.115+ — current async patterns, `Annotated[..., Depends(...)]` style.
- `uv` only for dependency management. `pyproject.toml` is source of truth, `uv.lock` is committed.
- Add deps with `uv add`; dev deps with `uv add --dev`.
- Every Python invocation goes through `uv run` (e.g. `uv run pytest`, `uv run uvicorn`). Never bare `python`, never bare `pytest`.

## Async-first

- Routes are `async def`. No sync DB calls in async routes.
- DB layer: SQLAlchemy 2.0 async with `asyncpg` driver.
- Outbound HTTP uses `httpx.AsyncClient`, NOT `requests`.

## Pydantic v2

- All request/response models are `pydantic.BaseModel` subclasses.
- Set `model_config = ConfigDict(extra="forbid")` on every shape that maps to a contract — unknown fields are bugs, not warnings.
- Field names match `contracts/schemas/*.json` exactly (snake_case).

## Settings

- `pydantic-settings.BaseSettings` for env vars. Never read `os.environ[...]` directly in app code.

## Module layout — one module per resource

```
app/
├── main.py              — FastAPI app factory + router registration
├── config.py            — Settings (pydantic-settings)
├── db.py                — async engine + session
├── schemas/             — Pydantic request/response models (mirror contracts/)
│   └── user.py
├── models/              — SQLAlchemy ORM models
│   └── user.py
├── routers/             — one router per resource
│   └── users.py
├── services/            — business logic, takes/returns plain types
│   ├── user_service.py
│   └── inference_client.py
└── alembic/             — migrations
```

## Migrations

- Alembic. `uv run alembic revision --autogenerate -m "..."` then `uv run alembic upgrade head`.
- One migration per schema-affecting change. Never edit an applied migration.

## Tests

- `pytest` + `pytest-asyncio`. Mark async tests with `@pytest.mark.asyncio`.
- Integration tests use `httpx.AsyncClient(transport=ASGITransport(app=app))` against the live app object.
- Integration DB tests use `testcontainers[postgres]` — no shared dev DB, no mocked sessions.
- Run with `cd apps/user-service && uv run pytest`.
