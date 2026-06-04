<!--
  Template for ONE experiment entry. The log-experiment skill appends a filled-in
  copy of this block to ml/docs/experiments/log.md after each run.
  Most-recent-at-bottom (the file reads as a journal).
-->

---

## {YYYY-MM-DD} — {experiment-name}

**MLflow run:** [`{run_id}`](http://localhost:5000/#/experiments/1/runs/{run_id})
**Run by:** {user or "automated"}
**Hypothesis:** {one-line — what was being tested}

### Setup

- Seed: `{42}`
- Model: `{e.g. LogisticRegression(C=1.0, max_iter=1000)}`
- Features: `[engagement_score, days_since_login, sessions_last_30d, support_tickets_last_90d]`
- Train/test split: `{0.75 / 0.25, random_state=42, stratified on y}`
- Dataset: `{ml/training/data/synthetic_users.csv or MLflow data artifact}`

### Params

| Param | Value |
|---|---|
| random_state | {42} |
| test_size | {0.25} |
| max_iter | {1000} |
| {param_n} | {value} |

### Metrics

| Metric | Value |
|---|---|
| accuracy | {0.9120} |
| precision | {0.8800} |
| recall | {0.8500} |
| f1 | {0.8647} |
| roc_auc | {0.9560} |

### Model artifact

`{model_path — e.g. /models/churn.joblib}`

### Outcome

{What happened. Did the hypothesis hold? What surprised you? What's the next experiment?}
