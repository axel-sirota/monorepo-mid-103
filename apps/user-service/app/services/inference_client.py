"""httpx wrapper around inference-gateway POST /predict."""
from __future__ import annotations

import httpx

from app.core.config import Settings, get_settings
from app.schemas.prediction import PredictionRequest, PredictionResponse


class InferenceGatewayError(RuntimeError):
    """Raised when the inference-gateway returns a non-2xx or is unreachable."""


class InferenceClient:
    def __init__(self, settings: Settings | None = None, client: httpx.AsyncClient | None = None):
        self._settings = settings or get_settings()
        self._client = client

    async def predict(self, payload: PredictionRequest) -> PredictionResponse:
        headers = {"X-API-Key": self._settings.inference_api_key}
        url = f"{self._settings.inference_gateway_url.rstrip('/')}/predict"

        client = self._client or httpx.AsyncClient(timeout=self._settings.inference_timeout_seconds)
        owns_client = self._client is None
        try:
            response = await client.post(url, json=payload.model_dump(), headers=headers)
        except httpx.HTTPError as exc:
            raise InferenceGatewayError(f"inference-gateway unreachable: {exc}") from exc
        finally:
            if owns_client:
                await client.aclose()

        if response.status_code >= 400:
            raise InferenceGatewayError(
                f"inference-gateway returned {response.status_code}: {response.text[:200]}"
            )

        return PredictionResponse.model_validate(response.json())
