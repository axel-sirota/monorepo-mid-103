"""One-shot churn model training script.

Reads data/synthetic_users.csv (auto-generates if missing), trains a sklearn
Pipeline (StandardScaler + LogisticRegression), logs to MLflow, and dumps the
joblib to MODEL_OUTPUT_PATH so the model-serving container can pick it up
from the shared /models volume.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from generate_data import (
    DEFAULT_OUTPUT as DEFAULT_DATA_PATH,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    write_csv,
)

RANDOM_STATE = 42
TEST_SIZE = 0.25
MAX_ITER = 1000


def load_or_generate_data(data_path: Path) -> pd.DataFrame:
    if not data_path.exists():
        write_csv(output_path=data_path)
    df = pd.read_csv(data_path)
    missing = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset {data_path} missing required columns: {missing}")
    return df


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(random_state=RANDOM_STATE, max_iter=MAX_ITER),
            ),
        ]
    )


def train(
    data_path: Path,
    model_output_path: Path,
    mlflow_tracking_uri: str,
    experiment_name: str = "churn",
) -> dict:
    """Train the churn pipeline end-to-end. Returns the JSON summary dict."""
    df = load_or_generate_data(data_path)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    pipeline = build_pipeline()

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_name = f"churn-{timestamp}"

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(
            {
                "random_state": RANDOM_STATE,
                "test_size": TEST_SIZE,
                "max_iter": MAX_ITER,
                "n_train_samples": int(len(X_train)),
                "n_test_samples": int(len(X_test)),
            }
        )

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, y_proba)),
        }
        mlflow.log_metrics(metrics)

        # Log model to MLflow. Don't fail the training run if the artifact upload
        # has a hiccup against a remote tracking server — the joblib is the
        # canonical artifact for model-serving.
        try:
            mlflow.sklearn.log_model(pipeline, artifact_path="model")
        except Exception as exc:  # pragma: no cover - defensive
            print(f"WARN: mlflow.sklearn.log_model failed: {exc}", file=sys.stderr)

        model_output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, model_output_path)

        summary = {
            "run_id": run.info.run_id,
            "model_path": str(model_output_path),
            "accuracy": round(metrics["accuracy"], 4),
            "roc_auc": round(metrics["roc_auc"], 4),
        }
        return summary


def main() -> int:
    mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "file://./mlruns")
    model_output_path = Path(os.environ.get("MODEL_OUTPUT_PATH", "/models/churn.joblib"))
    data_path = Path(os.environ.get("TRAINING_DATA_PATH", str(DEFAULT_DATA_PATH)))

    summary = train(
        data_path=data_path,
        model_output_path=model_output_path,
        mlflow_tracking_uri=mlflow_tracking_uri,
    )
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
