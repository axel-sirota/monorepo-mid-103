"""Pydantic v2 models for inference-gateway /predict."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    user_id: int = Field(ge=1)
    engagement_score: float = Field(ge=0.0, le=1.0)
    days_since_login: int = Field(ge=0)
    sessions_last_30d: int = Field(ge=0)
    support_tickets_last_90d: int = Field(ge=0)


class PredictionResponse(BaseModel):
    user_id: int = Field(ge=1)
    churn_probability: float = Field(ge=0.0, le=1.0)
    risk_band: Literal["low", "medium", "high"] | None = None
    model_version: str
