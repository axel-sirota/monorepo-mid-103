"""Tests for generate_data.py — primarily determinism + schema."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from generate_data import (
    ALL_COLUMNS,
    FEATURE_COLUMNS,
    N_ROWS,
    TARGET_COLUMN,
    generate_dataframe,
    write_csv,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_generate_dataframe_schema_and_size():
    df = generate_dataframe()
    assert list(df.columns) == ALL_COLUMNS
    assert len(df) == N_ROWS
    assert set(df[TARGET_COLUMN].unique()).issubset({0, 1})
    # Sanity on features
    assert df["engagement_score"].between(0.0, 1.0).all()
    assert (df["days_since_login"] >= 0).all()
    assert (df["sessions_last_30d"] >= 0).all()
    assert (df["support_tickets_last_90d"] >= 0).all()


def test_feature_columns_order_matches_contract():
    # The model-serving service consumes features in this exact order.
    assert FEATURE_COLUMNS == [
        "engagement_score",
        "days_since_login",
        "sessions_last_30d",
        "support_tickets_last_90d",
    ]


def test_generate_data_is_deterministic(tmp_path: Path):
    out1 = tmp_path / "a.csv"
    out2 = tmp_path / "b.csv"
    write_csv(output_path=out1)
    write_csv(output_path=out2)
    assert _sha256(out1) == _sha256(out2), "Two runs must produce byte-identical CSVs"


def test_generated_dataframe_has_both_classes():
    df = generate_dataframe()
    counts = df[TARGET_COLUMN].value_counts()
    assert 0 in counts.index and 1 in counts.index
    # No class should be vanishingly small (sanity for stratified split + AUC)
    assert counts.min() >= 20


def test_csv_roundtrip_preserves_schema(tmp_path: Path):
    out = tmp_path / "roundtrip.csv"
    write_csv(output_path=out)
    df = pd.read_csv(out)
    assert list(df.columns) == ALL_COLUMNS
    assert len(df) == N_ROWS
