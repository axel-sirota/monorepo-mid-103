"""Integration: GET /health hits the real (testcontainer) DB."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_health_returns_ok_with_db_ok(app_client):
    response = await app_client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "db": "ok"}
