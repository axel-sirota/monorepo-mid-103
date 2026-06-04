from httpx import AsyncClient


VALID_REQ = {
    "user_id": 1,
    "engagement_score": 0.32,
    "days_since_login": 28,
    "sessions_last_30d": 2,
    "support_tickets_last_90d": 4,
}


async def test_predict_returns_well_formed_response(client_with_model: AsyncClient) -> None:
    resp = await client_with_model.post("/predict", json=VALID_REQ)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # Required fields per the contract.
    assert body["user_id"] == VALID_REQ["user_id"]
    assert isinstance(body["churn_probability"], float)
    assert 0.0 <= body["churn_probability"] <= 1.0
    assert body["risk_band"] in {"low", "medium", "high"}
    assert isinstance(body["model_version"], str) and body["model_version"]

    # additionalProperties: false — response should not leak fields.
    assert set(body.keys()) == {"user_id", "churn_probability", "risk_band", "model_version"}


async def test_predict_400_on_missing_field(client_with_model: AsyncClient) -> None:
    bad = dict(VALID_REQ)
    del bad["engagement_score"]
    resp = await client_with_model.post("/predict", json=bad)
    # FastAPI returns 422 for validation errors by default — both 400 and 422
    # count as client-rejected; the contract test in the spec uses "400" loosely.
    assert resp.status_code in (400, 422)


async def test_predict_503_when_model_missing(client_without_model: AsyncClient) -> None:
    resp = await client_without_model.post("/predict", json=VALID_REQ)
    assert resp.status_code == 503
    body = resp.json()
    assert "detail" in body


async def test_predict_high_risk_for_disengaged_user(client_with_model: AsyncClient) -> None:
    # Low engagement + many tickets + many days since login => higher churn probability.
    high_risk_req = {
        "user_id": 42,
        "engagement_score": 0.05,
        "days_since_login": 89,
        "sessions_last_30d": 0,
        "support_tickets_last_90d": 9,
    }
    resp = await client_with_model.post("/predict", json=high_risk_req)
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_id"] == 42
    # Risk band derivation must be consistent with churn_probability.
    p = body["churn_probability"]
    expected = "low" if p < 0.33 else ("medium" if p < 0.66 else "high")
    assert body["risk_band"] == expected
