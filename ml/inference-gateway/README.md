# inference-gateway

A small Go/Gin proxy in front of `ml/model-serving`. Adds API-key auth and per-key
token-bucket rate limiting. Stateless — no database.

## Endpoints

- `GET /health` — `200 {"status":"ok"}`. No auth.
- `POST /predict` — requires `X-API-Key`, rate-limited per key. Body is the
  `PredictionRequest` defined in `contracts/schemas/prediction.json`. Proxies to
  `MODEL_SERVING_URL/predict` and returns the upstream response verbatim.

### Auth

Send the configured key in the `X-API-Key` header. Missing or wrong key → `401`.

### Rate limit

Per API key. `RATE_LIMIT_PER_MINUTE` tokens/min (default 60), with a burst of
`max(RATE_LIMIT_PER_MINUTE/6, 1)`. On overflow → `429 {"error":"rate_limit_exceeded"}`.

## Environment variables

| Var | Required | Default | Meaning |
|---|---|---|---|
| `MODEL_SERVING_URL` | yes | — | e.g. `http://model-serving:9001` |
| `API_KEY` | yes | — | Key clients must send in `X-API-Key` |
| `RATE_LIMIT_PER_MINUTE` | no | `60` | Per-key tokens per minute |
| `LOG_LEVEL` | no | `info` | `info` or `debug` |
| `PORT` | no | `9000` | HTTP listen port |

## Run standalone

```bash
export MODEL_SERVING_URL=http://localhost:9001
export API_KEY=dev-key
go run ./cmd/server
```

## Run tests

```bash
go test ./... -count=1
```

All tests are self-contained — no Docker or live upstream required (the upstream
is mocked via the `client.ModelServingClient` interface).
