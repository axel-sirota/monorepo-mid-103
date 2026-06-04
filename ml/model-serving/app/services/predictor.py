from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.schemas.prediction import PredictionRequest, PredictionResponse, RiskBand

log = logging.getLogger(__name__)

# Column order MUST match the contract used by the training service.
FEATURE_ORDER = (
    "engagement_score",
    "days_since_login",
    "sessions_last_30d",
    "support_tickets_last_90d",
)


def load_model(model_path: str) -> Any | None:
    """Load a joblib-serialized sklearn estimator. Returns None if missing/unloadable."""
    path = Path(model_path)
    if not path.exists():
        log.warning("Model file not found at %s; service will run without predictions.", path)
        return None
    try:
        model = joblib.load(path)
        log.info("Loaded model from %s (%s)", path, type(model).__name__)
        return model
    except Exception:  # noqa: BLE001
        log.exception("Failed to load model from %s", path)
        return None


def _risk_band(p: float) -> RiskBand:
    if p < 0.33:
        return "low"
    if p < 0.66:
        return "medium"
    return "high"


class Predictor:
    """Thin wrapper around a loaded sklearn estimator."""

    def __init__(self, model: Any, model_version: str) -> None:
        self._model = model
        self._model_version = model_version

    def predict(self, req: PredictionRequest) -> PredictionResponse:
        x = np.array(
            [[getattr(req, name) for name in FEATURE_ORDER]],
            dtype=float,
        )
        proba = self._model.predict_proba(x)
        # predict_proba returns shape (n_samples, n_classes); class 1 = churn.
        churn_p = float(proba[0, 1])
        # Numeric safety: clamp into [0, 1] to satisfy the response schema even if
        # the upstream estimator emits a marginally-out-of-range float.
        churn_p = max(0.0, min(1.0, churn_p))
        return PredictionResponse(
            user_id=req.user_id,
            churn_probability=churn_p,
            risk_band=_risk_band(churn_p),
            model_version=self._model_version,
        )
