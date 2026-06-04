"""Unit tests — pure logic, no DB, no network."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.schemas.prediction import PredictionRequest
from app.schemas.user import UserCreate
from app.services.user_service import user_to_prediction_request


def _fake_user(**overrides):
    base = dict(
        id=42,
        email="ada@example.com",
        full_name="Ada Lovelace",
        created_at=datetime(2026, 1, 15, 9, 30, tzinfo=timezone.utc),
        engagement_score=0.82,
        days_since_login=2,
        sessions_last_30d=17,
        support_tickets_last_90d=0,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_user_to_prediction_request_maps_all_features():
    user = _fake_user()
    req = user_to_prediction_request(user)

    assert isinstance(req, PredictionRequest)
    assert req.user_id == 42
    assert req.engagement_score == 0.82
    assert req.days_since_login == 2
    assert req.sessions_last_30d == 17
    assert req.support_tickets_last_90d == 0


def test_user_to_prediction_request_passes_through_high_risk_features():
    user = _fake_user(
        id=7,
        engagement_score=0.05,
        days_since_login=90,
        sessions_last_30d=0,
        support_tickets_last_90d=12,
    )
    req = user_to_prediction_request(user)

    assert req.user_id == 7
    assert req.engagement_score == 0.05
    assert req.days_since_login == 90
    assert req.sessions_last_30d == 0
    assert req.support_tickets_last_90d == 12


def test_user_create_defaults_are_sensible():
    payload = UserCreate(email="new@example.com")

    assert payload.full_name is None
    assert payload.engagement_score == 0.5
    assert payload.days_since_login == 0
    assert payload.sessions_last_30d == 0
    assert payload.support_tickets_last_90d == 0


# BUG: class-bug-11 — test has no assertion; it constructs an object but never checks anything
# (test-quality: no-op test, always passes regardless of correctness)
def test_user_creation():
    user = UserCreate(email="test@test.com", engagement_score=0.5)
    # missing assert — this test proves nothing


# BUG: class-bug-12 — mutation-weak test; passes even if + is replaced with * (2*3=6 > 0)
# (test-quality: weak oracle, should assert exact value not just sign)
def test_add_positive():
    a, b = 2, 3
    result = a + b
    assert result > 0  # survives mutation: a * b = 6 > 0 also passes
