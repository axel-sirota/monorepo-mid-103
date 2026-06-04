---
paths:
  - "apps/notification-service/**/*.go"
---

# Go / Gin conventions (notification-service)

Loaded when Claude reads any Go file under `apps/notification-service/`. Engineer persona ships this in 102 lab 1, scoped to notification-service only.

## Runtime + deps

- Go 1.22+ (range-over-func, new `slices`/`maps` stdlib).
- Gin v1.10+ for HTTP routing.
- `sqlx` for DB (NOT `gorm` — sqlx is the project standard; explicit queries beat magic).
- `golang-migrate` for schema migrations.

## Module layout

```
cmd/server/main.go        — entrypoint; wires config, deps, router, runs
internal/
├── handler/              — HTTP handlers; thin; map Gin context to service inputs
├── service/              — business logic; plain Go types in/out
├── repository/           — DB access via sqlx
├── model/                — DTOs matching contracts/schemas/*.json
├── middleware/           — auth, rate-limit, logging
└── config/               — env loading (envconfig or viper)
```

Tests live next to the code they test (`*_test.go` in the same package).

## Errors

- Return `error` from service and repo functions. Wrap with `fmt.Errorf("operation: %w", err)`.
- Handlers map errors to HTTP status via a single helper (e.g. `respondError(c, err)`); don't sprinkle `c.JSON(500, ...)` across handlers.

## Context

- Every service and repo function takes `ctx context.Context` as the FIRST parameter. Propagate from Gin via `c.Request.Context()` — a client disconnect cancels downstream work.

## Concurrency

- Use `errgroup` (`golang.org/x/sync/errgroup`) for parallel work. Never raw goroutines without a wait/error path.

## DTOs

- Struct field names use Go camelCase; JSON tags carry the contract's snake_case name: `` `json:"field_from_contract"` ``.
- Match `contracts/schemas/*.json` exactly. Drift is a bug.

## Tests

- `testify/assert` for assertions, `testcontainers-go` for DB integration tests.
- Handler tests use `httptest.NewRecorder` + `gin.New()` with the route under test wired in isolation.
- Test naming: `Test{Function}_{Scenario}_{Expected}`.
- Run with `cd apps/notification-service && go test ./...`.
