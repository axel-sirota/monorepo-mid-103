# user-service

Python FastAPI service owning the `users` table. Exposes a churn-risk endpoint that proxies to the `inference-gateway`.

## Stack

Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · asyncpg · Alembic · Pydantic v2 · httpx · uv

## Run standalone

```bash
uv sync --all-groups
uv run uvicorn app.main:app --reload --port 8001
```

OpenAPI docs at <http://localhost:8001/docs>.

## Run tests

```bash
uv run pytest             # full suite (needs Docker for testcontainers)
uv run pytest tests/unit  # unit only, no Docker needed
```

## Env vars

| Var | Required | Default | Notes |
| --- | --- | --- | --- |
| `DATABASE_URL` | yes | — | Async URL, e.g. `postgresql+asyncpg://user:pw@host:5432/users_db` |
| `INFERENCE_GATEWAY_URL` | yes | — | Base URL of `inference-gateway` |
| `INFERENCE_API_KEY` | yes | — | Sent as `X-API-Key` header |
| `LOG_LEVEL` | no | `INFO` | |
| `RUN_MIGRATIONS_ON_STARTUP` | no | `true` | Set `false` to skip auto-migrate |

## Endpoints

- `GET  /health` — liveness; always 200; reports DB status.
- `POST /users` — create a user.
- `GET  /users/{id}` — fetch a user (404 if missing).
- `GET  /users/{id}/churn-risk` — proxy to `inference-gateway` `/predict`.

## Migrations (manual)

```bash
uv run alembic upgrade head
uv run alembic revision -m "describe change" --autogenerate
```

By default the app runs `alembic upgrade head` automatically on startup.
