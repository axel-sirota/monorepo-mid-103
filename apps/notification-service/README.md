# notification-service

Go/Gin service that sends transactional email and logs every attempt to Postgres.

## Endpoints

- `GET /health` — liveness probe. Always returns `200 {"status":"ok"}`.
- `POST /notify` — body is a `Notification` JSON; returns `202 {"id":<log_id>}` on success or `502` on SMTP failure.

The request shape matches `contracts/schemas/notification.json`.

## Env vars (required)

| Var | Example |
|---|---|
| `DATABASE_URL` | `postgres://monorepo:monorepo@postgres:5432/notifications_db?sslmode=disable` |
| `SMTP_HOST` | `mailhog` |
| `SMTP_PORT` | `1025` |
| `FROM_EMAIL` | `noreply@example.com` |
| `LOG_LEVEL` | `info` (optional, default `info`) |
| `PORT` | `8002` (optional, default `8002`) |
| `MIGRATIONS_PATH` | `file://./migrations` (optional; auto-detected) |

## Run standalone

```bash
go run ./cmd/server
```

Migrations are applied automatically on startup using `golang-migrate`'s Go API against `./migrations`.

## Tests

```bash
go test ./...
```

The `/notify` suite uses testcontainers-go to spin up a real Postgres. SMTP is mocked via an interface, so no Mailhog is needed for tests. If Docker isn't available the suite skips with a clear message.

## Run migrations manually

```bash
make migrate-up    # requires the `migrate` CLI on PATH
make migrate-down
```

## Build

```bash
make build         # outputs ./tmp/notification-service
docker build -t notification-service .
```
