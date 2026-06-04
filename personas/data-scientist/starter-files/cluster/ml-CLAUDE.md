# ml/ — ML pipeline cluster

Lazy-loaded by Claude Code when working with files under `ml/`. Root `/CLAUDE.md` still loads first.

## Three services + one trainer

| Subdir | Stack | Local port | Owns |
|---|---|---|---|
| `training/` | Python 3.12 / sklearn / MLflow / uv | (one-shot) | trains + writes `/models/churn.joblib` |
| `model-serving/` | Python 3.12 / FastAPI / sklearn / uv | 9001 | loads joblib, exposes `POST /predict` |
| `inference-gateway/` | Go 1.22 / Gin / sqlx | 9000 | API-key auth + per-key rate limit, proxies to model-serving |

The trainer is a *one-shot* script — there's no long-running training service. It runs to completion, drops a joblib on the shared `/models/` volume, and exits. `docker-compose` also runs an MLflow tracking server on `http://localhost:5000` so training runs are recorded.

## Reproducibility is non-negotiable

Every stochastic call is seeded. `random_state=42` is the project default and is named `RANDOM_STATE` in `training/train.py`. Same number, same data, same code → same model. No exceptions:

- sklearn estimators take `random_state=RANDOM_STATE`.
- `numpy.random.seed(42)` whenever numpy randomness is used directly.
- `random.seed(42)` for stdlib `random`.
- Notebooks (`.ipynb`) MUST be executed top-to-bottom before commit (no `execution_count: null` cells, no out-of-order runs).

Dependencies are pinned via `uv.lock` (committed). Don't edit `pyproject.toml` without re-locking.

## MLflow first, files second

Every experiment logs to MLflow:

- Tracking URI: `http://localhost:5000` (compose service `mlflow`).
- Experiment name: `churn` (use this for all churn-model runs).
- Log params + metrics on every run via `mlflow.log_params(...)` + `mlflow.log_metrics(...)`.
- Log the trained model via `mlflow.sklearn.log_model(model, "model")`.
- `train.py` prints a JSON summary to stdout: `{"run_id": "...", "model_path": "...", "accuracy": ..., "roc_auc": ...}`. Capture this when invoking the `log-experiment` skill.

## Model card discipline

Every shipped model has a card under `ml/docs/model-cards/{model-name}-{version}.md`. Required sections: purpose, training data, performance metrics, known limitations, bias considerations, deployment notes. "Shipped" = the joblib was copied to the shared `/models/` volume that `model-serving` reads at startup.

## Feature contract (training → serving)

`ml/model-serving/app/services/predictor.py` has a constant:

```python
FEATURE_ORDER = (
    "engagement_score",
    "days_since_login",
    "sessions_last_30d",
    "support_tickets_last_90d",
)
```

Training MUST produce a model whose `predict_proba` accepts an array with columns in *exactly* that order. If you add a feature in training, you MUST update `FEATURE_ORDER` AND `contracts/schemas/prediction.json` AND `ml/model-serving/app/schemas/prediction.py` in the same change.

## Model artifact path

`MODEL_OUTPUT_PATH` env var, defaults to `/models/churn.joblib`. In `docker compose`, that's the `models-data` volume shared between `training` and `model-serving`. Never hardcode paths in scripts.

## Prediction contract

Source of truth: `contracts/schemas/prediction.json`. Consumed by `apps/user-service` (Python schemas) AND `ml/inference-gateway` (Go model). Changing the prediction contract is a cross-cluster move — coordinate with the engineer. That coordination is an Agent Teams scenario for Course 103, not 102.

## Tests

```bash
make test-ml                                  # all three services
cd ml/model-serving && uv run pytest -x
cd ml/training && uv run pytest -x
cd ml/inference-gateway && go test ./... -count=1
```

Always `uv run`, never bare `python` or `pytest`.

## Active subagent

`data-scientist-ml` — scoped to this cluster (+ read access to `apps/user-service` for end-to-end verification).

## Skill

`/log-experiment` — appends a structured entry to `ml/docs/experiments/log.md`, verifies the MLflow run, and dispatches a verifier sub-subagent that confirms the joblib artifact landed.
