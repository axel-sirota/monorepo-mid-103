# model-serving

FastAPI inference service that loads a scikit-learn churn-probability model from
disk on startup and exposes `POST /predict`. No database.

## Endpoints

- `GET /health` — always 200; body reports whether the model is loaded.
- `POST /predict` — returns churn probability + risk band; 503 if model missing.

## Env vars

| Name         | Default                 | Description                          |
|--------------|-------------------------|--------------------------------------|
| `MODEL_PATH` | `/models/churn.joblib`  | Path to the joblib-serialized model. |
| `LOG_LEVEL`  | `INFO`                  | Python logging level.                |
| `MODEL_VERSION` | `v1`                 | Returned in PredictionResponse.      |

## Run standalone (local)

```bash
uv sync --all-groups
MODEL_PATH=/tmp/churn.joblib uv run uvicorn app.main:app --host 0.0.0.0 --port 9001
```

`MODEL_PATH` must point at a joblib file containing a sklearn estimator (or
Pipeline) that supports `predict_proba` on a `(1, 4)` array with columns:
`[engagement_score, days_since_login, sessions_last_30d, support_tickets_last_90d]`.

If the file is missing the service still starts and `/health` returns
`{"status":"ok","model":"missing"}` — but `/predict` will 503.

## Producing a model

See `ml/training` for the service that trains and writes `/models/churn.joblib`
into the shared `models-data` docker volume.

## Tests

```bash
uv sync --all-groups
uv run pytest -x
```

Tests build a tiny deterministic logistic-regression model in a temp dir; no
Docker or real model file required.
