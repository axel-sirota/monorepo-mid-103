"""Generate deterministic synthetic churn training data.

Produces data/synthetic_users.csv with ~500 rows of realistic churn features.
Feature order MUST match what ml/model-serving expects:
  [engagement_score, days_since_login, sessions_last_30d, support_tickets_last_90d]
Target column: churned (0/1).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "engagement_score",
    "days_since_login",
    "sessions_last_30d",
    "support_tickets_last_90d",
]
TARGET_COLUMN = "churned"
ALL_COLUMNS = FEATURE_COLUMNS + [TARGET_COLUMN]

N_ROWS = 500
SEED = 42

DEFAULT_OUTPUT = Path(__file__).parent / "data" / "synthetic_users.csv"


def generate_dataframe(n_rows: int = N_ROWS, seed: int = SEED) -> pd.DataFrame:
    """Generate a deterministic synthetic churn dataset.

    Distributions are crafted so high engagement -> low churn,
    low engagement + many support tickets -> high churn.
    """
    rng = np.random.default_rng(seed)

    # engagement_score: beta distribution skewed slightly toward middle/high
    engagement_score = rng.beta(2.0, 2.0, size=n_rows)

    # days_since_login: lower for engaged users, higher for disengaged
    # base from exponential, modulated inversely by engagement
    base_days = rng.exponential(scale=10.0, size=n_rows)
    days_since_login = np.clip(
        (base_days * (1.5 - engagement_score)).round().astype(int), 0, 180
    )

    # sessions_last_30d: poisson rate proportional to engagement
    sessions_last_30d = rng.poisson(lam=2.0 + engagement_score * 25.0).astype(int)

    # support tickets: poisson, slightly higher for disengaged users
    support_tickets_last_90d = rng.poisson(
        lam=0.5 + (1.0 - engagement_score) * 2.0
    ).astype(int)

    # Churn probability: monotonic in disengagement + tickets, anti-monotonic in sessions
    logit = (
        -2.5
        + 4.0 * (1.0 - engagement_score)
        + 0.04 * days_since_login
        - 0.06 * sessions_last_30d
        + 0.5 * support_tickets_last_90d
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    churned = (rng.uniform(size=n_rows) < prob).astype(int)

    df = pd.DataFrame(
        {
            "engagement_score": engagement_score.round(6),
            "days_since_login": days_since_login,
            "sessions_last_30d": sessions_last_30d,
            "support_tickets_last_90d": support_tickets_last_90d,
            "churned": churned,
        }
    )
    # Enforce column order
    return df[ALL_COLUMNS]


def write_csv(output_path: Path = DEFAULT_OUTPUT, n_rows: int = N_ROWS, seed: int = SEED) -> Path:
    """Generate and write the CSV. Returns the path written."""
    df = generate_dataframe(n_rows=n_rows, seed=seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Use deterministic formatting: no index, fixed line terminator
    df.to_csv(output_path, index=False, lineterminator="\n")
    return output_path


if __name__ == "__main__":
    path = write_csv()
    print(f"Wrote {path} with {N_ROWS} rows (seed={SEED}).")
