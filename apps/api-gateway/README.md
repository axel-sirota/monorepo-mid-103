# api-gateway

Java/Spring Boot front door. Validates an API key, proxies to `user-service` and
`notification-service`, handles cross-cutting concerns (logging, error mapping).

## Run standalone

```bash
./mvnw spring-boot:run
```

By default the app reads `USER_SERVICE_URL`, `NOTIFICATION_SERVICE_URL`, and `API_KEY`
from the environment. With nothing set it boots and serves `/health` but proxy calls
will fail since the upstream URLs default to localhost.

## Run tests

```bash
./mvnw test
```

Tests run offline (no Docker, no DB).

## Run via Docker (from monorepo root)

```bash
docker compose up api-gateway
```

## Endpoints

- `GET /health` — public, returns `{"status":"ok"}`.
- `GET /api/users/{id}` — requires `X-API-Key`; proxies user-service.
- `POST /api/users` — requires `X-API-Key`; proxies user-service; returns 201.
- `GET /api/users/{id}/churn-risk` — requires `X-API-Key`; proxies user-service.
- `POST /api/notify` — requires `X-API-Key`; proxies notification-service; returns 202.

## Env vars

| Var                       | Required | Example                          |
| ------------------------- | -------- | -------------------------------- |
| `USER_SERVICE_URL`        | yes      | `http://user-service:8001`       |
| `NOTIFICATION_SERVICE_URL`| yes      | `http://notification-service:8002` |
| `API_KEY`                 | yes      | `dev-key-change-me`              |
| `SPRING_PROFILES_ACTIVE`  | no       | `prod` or `dev`                  |
