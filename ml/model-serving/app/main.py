from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.predict import router as predict_router
from app.core.config import get_settings
from app.services.predictor import load_model


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    _configure_logging(settings.log_level)
    app.state.settings = settings
    app.state.model = load_model(settings.model_path)
    try:
        yield
    finally:
        app.state.model = None


app = FastAPI(
    title="model-serving",
    description="Churn-probability inference service.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(predict_router)
