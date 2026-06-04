# Data Scientist persona — pre-class setup

## Required

- Docker Desktop 25+ (MLflow runs in compose)
- Python 3.12 + `uv` for local notebook iteration
- Claude Code CLI
- `jq` 1.6+ (`brew install jq` on macOS, `apt-get install jq` on Linux) —
  used by the Lab 3 notebook-hygiene hook to parse `.ipynb` files

## Pre-class warm-up

```bash
cp .env.example .env
make up                            # brings up MLflow at http://localhost:5000
make train                         # runs one training cycle, you should see a run in MLflow
make predict                       # confirms the model serves predictions
```

Confirm an MLflow run appears at http://localhost:5000 with `params`, `metrics`, and a logged artifact.

Confirm `jq` works:

```bash
jq --version    # expected: jq-1.6 or newer
```
