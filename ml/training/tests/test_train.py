"""End-to-end smoke test for the training script."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from generate_data import FEATURE_COLUMNS, write_csv
from train import train


def test_training_end_to_end_writes_loadable_joblib(tmp_path: Path):
    data_path = tmp_path / "data" / "synthetic_users.csv"
    model_path = tmp_path / "model" / "churn.joblib"
    mlruns = tmp_path / "mlruns"
    mlflow_uri = "file://" + str(mlruns)

    # Seed the data file deterministically.
    write_csv(output_path=data_path)

    summary = train(
        data_path=data_path,
        model_output_path=model_path,
        mlflow_tracking_uri=mlflow_uri,
        experiment_name="test-churn",
    )

    # Summary contract
    assert set(summary.keys()) == {"run_id", "model_path", "accuracy", "roc_auc"}
    assert summary["model_path"] == str(model_path)
    assert isinstance(summary["run_id"], str) and summary["run_id"]
    assert 0.0 <= summary["accuracy"] <= 1.0
    assert 0.0 <= summary["roc_auc"] <= 1.0
    # The synthetic data has clear signal; demand a non-trivial model.
    assert summary["roc_auc"] > 0.7

    # Joblib exists and loads
    assert model_path.exists(), "joblib must be written to MODEL_OUTPUT_PATH"
    pipeline = joblib.load(model_path)
    assert hasattr(pipeline, "predict_proba"), "Loaded model must expose predict_proba"

    # Single-row prediction has shape (1, 2)
    sample = np.array([[0.85, 2, 18, 0]], dtype=float)
    proba = pipeline.predict_proba(sample)
    assert proba.shape == (1, 2)
    assert np.isclose(proba.sum(axis=1), 1.0).all()

    # MLflow tracking dir was populated
    assert mlruns.exists()
    assert any(mlruns.iterdir()), "MLflow file store should contain at least one entry"


def test_feature_column_count_matches_pipeline_expectation(tmp_path: Path):
    """The pipeline must accept exactly the contract feature columns."""
    data_path = tmp_path / "data.csv"
    model_path = tmp_path / "m.joblib"
    mlruns = tmp_path / "mlruns"
    write_csv(output_path=data_path)

    train(
        data_path=data_path,
        model_output_path=model_path,
        mlflow_tracking_uri="file://" + str(mlruns),
        experiment_name="test-churn-2",
    )

    pipeline = joblib.load(model_path)
    # Match feature count exactly
    n_features = len(FEATURE_COLUMNS)
    sample = np.zeros((3, n_features))
    proba = pipeline.predict_proba(sample)
    assert proba.shape == (3, 2)
