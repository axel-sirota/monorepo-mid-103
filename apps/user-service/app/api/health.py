"""GET /health — liveness probe."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import get_sessionmaker

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    db_status = "ok"
    try:
        sm = get_sessionmaker()
        async with sm() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "fail"
    return {"status": "ok", "db": db_status}
