from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Make `fixtures/` importable as a top-level package for tests.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fixtures.tiny_model_builder import build_tiny_model  # noqa: E402


@pytest.fixture
def tiny_model_path(tmp_path: Path) -> Path:
    """Train a tiny deterministic churn model and return its joblib path."""
    target = tmp_path / "churn.joblib"
    return build_tiny_model(target)


@pytest.fixture
def missing_model_path(tmp_path: Path) -> Path:
    """A path that intentionally does NOT exist."""
    return tmp_path / "no_such_model.joblib"


@asynccontextmanager
async def _build_client(model_path: Path) -> AsyncIterator[AsyncClient]:
    """Build a fresh FastAPI app pointed at ``model_path`` and yield a test client.

    We set ``MODEL_PATH`` in the process env before constructing the app so the
    Settings() instance built inside the lifespan reads our test path. We then
    manually drive the lifespan context so ``app.state.model`` / ``settings``
    are populated.
    """
    import os

    from app.main import app as fastapi_app

    prev = os.environ.get("MODEL_PATH")
    os.environ["MODEL_PATH"] = str(model_path)
    try:
        async with fastapi_app.router.lifespan_context(fastapi_app):
            async with AsyncClient(
                transport=ASGITransport(app=fastapi_app),
                base_url="http://test",
            ) as ac:
                yield ac
    finally:
        if prev is None:
            os.environ.pop("MODEL_PATH", None)
        else:
            os.environ["MODEL_PATH"] = prev


@pytest_asyncio.fixture
async def client_with_model(tiny_model_path: Path) -> AsyncIterator[AsyncClient]:
    async with _build_client(tiny_model_path) as ac:
        yield ac


@pytest_asyncio.fixture
async def client_without_model(missing_model_path: Path) -> AsyncIterator[AsyncClient]:
    async with _build_client(missing_model_path) as ac:
        yield ac
