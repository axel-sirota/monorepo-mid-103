# training

One-shot Python script that trains a scikit-learn churn model, logs the run to
MLflow, and writes a joblib to the shared `/models` volume where
`ml/model-serving` reads it.

This is **not** a long-running service. It runs to completion, then exits.

## What it does

1. Loads `data/synthetic_users.csv` (auto-generates deterministically if missing)
2. 75/25 train/test split, `random_state=42`
3. `Pipeline(StandardScaler -> LogisticRegression(max_iter=1000, random_state=42))`
4. Logs params, metrics (`accuracy`, `precision`, `recall`, `f1`, `roc_auc`) and the
   model to MLflow under experiment `churn`
5. Dumps the fitted pipeline to `MODEL_OUTPUT_PATH` via `joblib.dump`
6. Prints a single-line JSON summary to stdout

## Feature contract

The pipeline expects exactly these columns, in this order — matching what
`ml/model-serving` sends at inference time:

```
[engagement_score, days_since_login, sessions_last_30d, support_tickets_last_90d]
```

Target: `churned` (0/1).

## Run via Docker (from monorepo root)

```bash
make train
# or
docker compose --profile training run --rm training
```

The `training` profile means this service stays dormant under normal
`docker compose up` and only runs on demand.

## Run locally

```bash
cd ml/training
uv sync --all-groups
uv run python generate_data.py           # (re)generate data/synthetic_users.csv
MLFLOW_TRACKING_URI=file://./mlruns \
MODEL_OUTPUT_PATH=./tmp_model.joblib \
  uv run python train.py
uv run pytest -x
```

## Environment variables

| Var                    | Default                  | Purpose                                  |
| ---------------------- | ------------------------ | ---------------------------------------- |
| `MLFLOW_TRACKING_URI`  | `file://./mlruns`        | MLflow server or local file store        |
| `MODEL_OUTPUT_PATH`    | `/models/churn.joblib`   | Where to dump the joblib                 |
| `TRAINING_DATA_PATH`   | `./data/synthetic_users.csv` | Input CSV (auto-generated if missing) |

## Output

stdout (single line, JSON):

```json
{"run_id": "abcd1234...", "model_path": "/models/churn.joblib", "accuracy": 0.91, "roc_auc": 0.96}
```

The joblib lands at `MODEL_OUTPUT_PATH`. In docker-compose, that's the
`models-data` volume which `ml/model-serving` also mounts.
