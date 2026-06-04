"""Integration: users CRUD round-trip + churn-risk with mocked inference-gateway."""
from __future__ import annotations

import httpx
import pytest
import respx

pytestmark = pytest.mark.asyncio


async def test_create_then_get_user_round_trips(app_client):
    create_resp = await app_client.post(
        "/users",
        json={"email": "ada@example.com", "full_name": "Ada Lovelace"},
    )
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()

    assert created["email"] == "ada@example.com"
    assert created["full_name"] == "Ada Lovelace"
    assert created["engagement_score"] == 0.5
    assert created["days_since_login"] == 0
    assert created["id"] >= 1

    get_resp = await app_client.get(f"/users/{created['id']}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["email"] == "ada@example.com"
    assert fetched["id"] == created["id"]


async def test_get_user_missing_returns_404(app_client):
    resp = await app_client.get("/users/999999")
    assert resp.status_code == 404


async def test_churn_risk_calls_inference_gateway_with_api_key(app_client):
    create_resp = await app_client.post(
        "/users",
        json={
            "email": "bob@example.com",
            "full_name": "Bob",
            "engagement_score": 0.32,
            "days_since_login": 28,
            "sessions_last_30d": 2,
            "support_tickets_last_90d": 4,
        },
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    with respx.mock(assert_all_called=True) as mock:
        route = mock.post(url__regex=r"^http://.+/predict$").mock(
            return_value=httpx.Response(
                200,
                json={
                    "user_id": user_id,
                    "churn_probability": 0.81,
                    "risk_band": "high",
                    "model_version": "v1",
                },
            )
        )

        resp = await app_client.get(f"/users/{user_id}/churn-risk")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["user_id"] == user_id
    assert body["churn_probability"] == 0.81
    assert body["risk_band"] == "high"
    assert body["model_version"] == "v1"

    # Inspect the outbound request: must carry X-API-Key + the user's features.
    assert route.called
    sent = route.calls.last.request
    assert sent.headers.get("x-api-key") == "dev-key-change-me"
    import json as _json

    payload = _json.loads(sent.content)
    assert payload["user_id"] == user_id
    assert payload["engagement_score"] == 0.32
    assert payload["days_since_login"] == 28
    assert payload["sessions_last_30d"] == 2
    assert payload["support_tickets_last_90d"] == 4


async def test_churn_risk_user_not_found(app_client):
    resp = await app_client.get("/users/999999/churn-risk")
    assert resp.status_code == 404
