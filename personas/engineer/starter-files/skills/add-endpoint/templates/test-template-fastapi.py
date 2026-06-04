# Template: copy into apps/user-service/tests/integration/test_{{NAME}}_api.py
# Replace {{NAME}}, {{METHOD}} (lowercase: get/post/put/delete), {{ENDPOINT}}, {{EXPECTED_STATUS}}.
# Assertion bodies should reflect the shape in contracts/schemas/*.json — not just "endpoint exists".

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_{{METHOD}}_{{NAME}}_returns_{{EXPECTED_STATUS}}():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.{{METHOD}}(
            "{{ENDPOINT}}",
            json={"field_from_contract": "value"},  # match contracts/schemas/*.json
            headers={"X-API-Key": "test-key"},
        )

    assert response.status_code == {{EXPECTED_STATUS}}
    body = response.json()
    assert "field_from_contract" in body  # assert real shape, not just status
