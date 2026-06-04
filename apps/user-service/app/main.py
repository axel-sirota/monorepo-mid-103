"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.config import get_settings
from app.db.session import dispose_engine, init_engine


def _run_migrations(database_url: str) -> None:
    cfg = AlembicConfig("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    log = logging.getLogger("user-service")

    init_engine(settings.database_url)

    if settings.run_migrations_on_startup:
        try:
            _run_migrations(settings.database_url)
        except Exception as exc:  # noqa: BLE001
            log.warning("alembic upgrade failed at startup: %s", exc)

    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(
    title="user-service",
    description="Owns the users table; proxies churn-risk inference.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(users_router)
