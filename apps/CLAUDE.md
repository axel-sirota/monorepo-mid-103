# apps/ — backend cluster

Lazy-loaded by Claude Code when working with files under `apps/`. Root `/CLAUDE.md` still loads first.

## The three services

| Service | Stack | Local port | Owns |
|---|---|---|---|
| `api-gateway` | Java 21 / Spring Boot 3.4 / Maven | 8080 | API key auth, proxy routing |
| `user-service` | Python 3.12 / FastAPI / uv | 8001 | `users` table, churn-risk fetch |
| `notification-service` | Go 1.22 / Gin / sqlx | 8002 | `notification_log` table, SMTP send |

## Dependency graph

```
api-gateway ──▶ user-service ──▶ inference-gateway (ml/)
            └─▶ notification-service
```

The gateway proxies `/api/users/*` to user-service and `/api/notify` to notification-service. See per-service READMEs for exact endpoints. `user-service` calls `inference-gateway` in `ml/` for churn predictions — that call crosses cluster boundaries; the shape lives in `contracts/schemas/prediction.json`.

## Contracts policy

Every cross-service shape is hand-typed in EACH consumer service and MUST match `contracts/schemas/*.json`. The schemas are the source of truth at MID stage; at END stage they migrate to OpenAPI + codegen.

If you change a field shape in a consumer, you MUST verify the schema still matches. If the schema is wrong, fix it AND every other consumer in the same commit. Consumer map:

- `contracts/schemas/user.json` ← `apps/user-service/app/schemas/user.py`, `apps/api-gateway/.../model/UserDto.java`
- `contracts/schemas/notification.json` ← `apps/notification-service/internal/model/notification.go`, `apps/api-gateway/.../model/NotificationDto.java`
- `contracts/schemas/prediction.json` ← `ml/model-serving/app/schemas/prediction.py`, `ml/inference-gateway/internal/model/prediction.go`, `apps/user-service/app/services/inference_client.py`

If your change touches `prediction.json`, you're crossing into `ml/` — that's an Agent Teams scenario (103), not a 102 solo task. Stop and escalate.

## Test conventions

| Service | Command | Framework |
|---|---|---|
| api-gateway | `cd apps/api-gateway && ./mvnw -B test` | JUnit 5 + MockMvc + Testcontainers |
| user-service | `cd apps/user-service && uv run pytest` | pytest + pytest-asyncio + httpx ASGITransport |
| notification-service | `cd apps/notification-service && go test ./...` | testing + testify + testcontainers-go |

Or all three at once: `make test-apps`.

## Active subagent

`engineer-apps` is scoped to this cluster. Invoke explicitly with `@agent-engineer-apps`, or let auto-routing handle it when the user's task obviously lives in `apps/`.

## Hot reload

`make up-dev` brings everything up with hot reload (Spring DevTools, `uvicorn --reload`, `air` for Go). Use this for the inner dev loop — do NOT restart the stack to test a code change.

## DO NOT

- Don't put cross-service shared code in `apps/`. There is none; the gateway-to-service contract is HTTP.
- Don't touch `ml/` or `frontend/` from inside an `apps/` task — that's a cross-cluster coordination scenario covered in 103 (Agent Teams), not 102.
- Don't add a 4th service without updating this file, the root `docker-compose.yml`, and the root `CLAUDE.md`.
