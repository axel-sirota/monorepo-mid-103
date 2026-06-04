---
name: log-experiment
description: Log a completed ML experiment with seed/params/metrics to ml/docs/experiments/log.md AND to MLflow, then verify the artifact landed where expected. Use after a training run completes, when the user asks to "log this experiment", "record this run", or wraps up an iteration.
allowed-tools: Read, Edit, Write, Bash, Task
---

# log-experiment

You are recording a churn-model experiment for the data scientist. There is no "quick try without logging" — every experiment we run goes through this skill so the run is reproducible from the log alone.

## Step 1 — Gather context from the user

Ask the user (one prompt, all four fields — don't fabricate any of them):

1. **Experiment name** (kebab-case, e.g. `baseline-c1.0`, `try-higher-test-size`).
2. **One-line hypothesis** — what they were testing. ("Smaller train set hurts ROC-AUC", "C=0.5 reduces overfit", etc.)
3. **The training command they ran (or want you to run)** — typically `make train` or a direct `cd ml/training && uv run python train.py` invocation.
4. **Whether the run already happened** (yes/no). If yes, ask for the stdout/run_id; if no, you'll run it next.

If they only give you a name, prompt for the rest. Do NOT proceed with placeholders.

## Step 2 — Run training if not already run

If the user hasn't run it yet, run the command they gave you. Capture stdout. `train.py` always ends with a single JSON line of the form:

```json
{"run_id": "abc123def456", "model_path": "/models/churn.joblib", "accuracy": 0.9120, "roc_auc": 0.9560}
```

If the JSON line isn't there, training failed — surface the error to the user and STOP. Do not log a half-row.

## Step 3 — Parse the JSON summary

Extract `run_id`, `model_path`, `accuracy`, `roc_auc` from the JSON line. These are the four fields the log row needs at minimum.

## Step 4 — (Optional) Fetch full params + metrics from MLflow

If MLflow is reachable, fetch the full dict — the stdout summary only has 2 metrics, but MLflow has all 5 plus all params. Use a Python one-liner via `uv run python -c`:

```bash
cd ml/training && uv run python -c "
import mlflow, json, sys
mlflow.set_tracking_uri('http://localhost:5000')
run = mlflow.MlflowClient().get_run(sys.argv[1])
print(json.dumps({'params': run.data.params, 'metrics': run.data.metrics}))
" "$RUN_ID"
```

If this fails (MLflow not reachable), continue with only the JSON-summary fields. Note "MLflow unreachable — partial entry" in the row's Notes column.

## Step 5 — Append to `ml/docs/experiments/log.md`

The seed file (header + one example entry) is already present in the repo. Append the new entry BELOW any existing ones (most-recent-at-bottom is the convention; the file reads as a journal).

Use `${CLAUDE_SKILL_DIR}/templates/experiment-template.md` as the structure. Each entry includes: date, experiment name, MLflow run_id (linked to the MLflow UI URL `http://localhost:5000/#/experiments/1/runs/{run_id}`), seed, params summary, metrics summary, hypothesis, outcome, model_path.

If `ml/docs/experiments/log.md` does not exist (it should — seed file ships in the repo), create it with the same header the seed file uses.

## Step 6 — Dispatch a verifier sub-subagent

Use the `Task` tool to dispatch a sub-subagent that confirms the joblib actually landed:

```
Task(
  subagent_type="general-purpose",
  description="Verify ML artifact",
  prompt="Verify the joblib at <model_path> exists and is loadable. Run: ls -lh <model_path> to show file size and mtime, then uv run python -c \"import joblib; m = joblib.load('<model_path>'); print(type(m).__name__)\" to confirm it loads. Report file size, mtime, and the loaded class name. If the file is missing or not loadable, respond exactly 'ARTIFACT INVALID' and the error."
)
```

`general-purpose` is the safe choice — no custom verifier subagent ships with this persona, and that's intentional. Wait for the response.

If the verifier returns "ARTIFACT INVALID", the entry stays in the log BUT add a bold "FAILED VERIFICATION" line in the Outcome section. The log is append-only journal — false-positive runs are still data.

## Step 7 — Report to the user

Print exactly:

```
Experiment logged.

  Name:        <experiment-name>
  Hypothesis:  <one-line>
  MLflow run:  http://localhost:5000/#/experiments/1/runs/<run_id>
  Accuracy:    <0.9120>
  ROC-AUC:     <0.9560>
  Artifact:    <model_path> (<size>, <mtime>) — <loaded class name>
  Log entry:   ml/docs/experiments/log.md (appended)
  Verifier:    PASS  (or FAIL with reason)
```

## DO NOT

- Do NOT fabricate metrics, params, or run_ids. If a value is missing, ask the user.
- Do NOT call `mlflow` CLI commands that mutate runs (delete, rename, etc.). Read-only.
- Do NOT skip the verifier dispatch — the whole point of the skill is independent confirmation that what training claimed actually happened.
- Do NOT proceed if the user hasn't given you the hypothesis. The Notes / Outcome sections are what make the log readable a month later.
