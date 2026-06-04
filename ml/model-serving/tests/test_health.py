from httpx import AsyncClient


async def test_health_returns_ok_with_model_loaded(client_with_model: AsyncClient) -> None:
    resp = await client_with_model.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "ok", "model": "loaded"}


async def test_health_returns_ok_when_model_missing(client_without_model: AsyncClient) -> None:
    resp = await client_without_model.get("/health")
    # Healthcheck must always be 200; the body indicates whether predictions work.
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "ok", "model": "missing"}
