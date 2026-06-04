"""Shared pytest fixtures.

Integration tests spin up a real PostgreSQL via testcontainers (one container
per session). Each test runs against a freshly migrated schema.

If Docker is not available, integration tests are skipped at collection time.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest

# Detect Docker availability early so we can skip the heavy fixtures cleanly.
try:
    import docker  # noqa: F401
    from testcontainers.postgres import PostgresContainer

    _DOCKER_IMPORTABLE = True
except Exception:  # noqa: BLE001
    _DOCKER_IMPORTABLE = False


def _docker_available() -> bool:
    if not _DOCKER_IMPORTABLE:
        return False
    try:
        import docker as _docker

        _docker.from_env().ping()
        return True
    except Exception:  # noqa: BLE001
        return False


DOCKER_AVAILABLE = _docker_available()


def pytest_collection_modifyitems(config, items):
    if DOCKER_AVAILABLE:
        return
    skip_marker = pytest.mark.skip(reason="Docker not available; integration tests skipped")
    for item in items:
        if "integration" in str(item.fspath).replace("\\", "/").split("/"):
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """Session-scoped PostgreSQL container; yields an asyncpg URL."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker not available")

    with PostgresContainer("postgres:16.3-alpine") as pg:
        sync_url = pg.get_connection_url()
        # testcontainers returns e.g. postgresql+psycopg2://... -> swap to asyncpg
        async_url = sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
        async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
        yield async_url


@pytest.fixture(scope="session", autouse=False)
def _migrated_schema(postgres_url: str) -> Iterator[str]:
    """Run alembic upgrade head once per session against the testcontainer."""
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["RUN_MIGRATIONS_ON_STARTUP"] = "false"

    # Reset cached settings so the new env vars are picked up.
    from app.core.config import get_settings

    get_settings.cache_clear()

    from alembic import command
    from alembic.config import Config as AlembicConfig

    cfg = AlembicConfig("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", postgres_url)
    command.upgrade(cfg, "head")
    yield postgres_url


@pytest.fixture()
async def app_client(_migrated_schema: str) -> AsyncIterator:
    """ASGI client wired to the migrated test database."""
    from httpx import ASGITransport, AsyncClient

    # Late import: ensures env vars are set before settings cache is populated.
    from app.db.session import dispose_engine, init_engine
    from app.main import app

    init_engine(_migrated_schema)

    # Truncate users between tests to keep tests independent.
    from sqlalchemy import text

    from app.db.session import get_sessionmaker

    sm = get_sessionmaker()
    async with sm() as session:
        await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY"))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    await dispose_engine()
