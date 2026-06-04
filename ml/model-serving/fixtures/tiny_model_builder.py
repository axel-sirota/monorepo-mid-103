"""Build a tiny deterministic churn model for tests.

Trains a logistic regression on 50 rows of synthetic data using the same
feature order the predictor expects:
    [engagement_score, days_since_login, sessions_last_30d, support_tickets_last_90d]
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression


def build_tiny_model(out_path: Path) -> Path:
    rng = np.random.default_rng(seed=42)
    n = 50

    engagement = rng.uniform(0.0, 1.0, size=n)
    days_since_login = rng.integers(0, 90, size=n)
    sessions = rng.integers(0, 40, size=n)
    tickets = rng.integers(0, 10, size=n)

    X = np.column_stack([engagement, days_since_login, sessions, tickets]).astype(float)

    # Deterministic label: high churn likelihood when engagement is low and
    # support tickets are many. Sigmoid-ish rule with noise from the rng.
    logits = -3.0 * engagement + 0.04 * days_since_login - 0.05 * sessions + 0.5 * tickets
    probs = 1.0 / (1.0 + np.exp(-logits))
    y = (probs > 0.5).astype(int)
    # Guarantee both classes are present so LogisticRegression doesn't choke.
    if y.sum() == 0:
        y[0] = 1
    if y.sum() == len(y):
        y[0] = 0

    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X, y)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_path)
    return out_path


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/churn.joblib")
    p = build_tiny_model(target)
    print(f"wrote {p}")
