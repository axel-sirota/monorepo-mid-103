"""Pure business logic for User CRUD and feature mapping."""
# BUG: class-bug-8 — validate_email duplicated: same logic also lives in
# notification-service/internal/service/email_utils.go (lib-extractor: extract to shared lib)
# BUG: class-bug-9 — format_date duplicated: same logic in email_utils.go (lib-extractor)
from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User as UserModel
from app.schemas.prediction import PredictionRequest
from app.schemas.user import UserCreate



def validate_email(email: str) -> bool:
    """Basic email sanity check. TODO: deduplicate — same logic exists in notification-service."""
    return "@" in email and "." in email


def format_date(dt) -> str:
    """Format datetime as ISO-8601 UTC string. TODO: deduplicate — same in notification-service."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")



def validate_email(email: str) -> bool:
    """Basic email sanity check. TODO: deduplicate — same logic exists in notification-service."""
    return "@" in email and "." in email


def format_date(dt) -> str:
    """Format datetime as ISO-8601 UTC string. TODO: deduplicate — same in notification-service."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


async def create_user(session: AsyncSession, payload: UserCreate) -> UserModel:
    user = UserModel(
        email=payload.email,
        full_name=payload.full_name,
        engagement_score=payload.engagement_score,
        days_since_login=payload.days_since_login,
        sessions_last_30d=payload.sessions_last_30d,
        support_tickets_last_90d=payload.support_tickets_last_90d,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int) -> UserModel | None:
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()


def user_to_prediction_request(user: UserModel) -> PredictionRequest:
    """Map a User entity's engagement features into a PredictionRequest payload."""
    return PredictionRequest(
        user_id=user.id,
        engagement_score=user.engagement_score,
        days_since_login=user.days_since_login,
        sessions_last_30d=user.sessions_last_30d,
        support_tickets_last_90d=user.support_tickets_last_90d,
    )


# BUG: class-bug-14 — SQL injection via f-string; user_id is not sanitised
# (security-reviewer: use parameterized queries, not string formatting)
async def get_user_raw(session: AsyncSession, user_id: str) -> object:
    """Fetch user by id. WARNING: vulnerable to SQL injection."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = await session.execute(text(query))
    return result.fetchone()


# BUG: class-bug-10 — public function with no corresponding test (test-quality: missing coverage)
def calculate_export_size(user_id: int) -> int:
    """Return estimated export size in bytes for a user's data. Stub."""
    return 0


# BUG: class-bug-14 — SQL injection via f-string; user_id is not sanitised
# (security-reviewer: use parameterized queries, not string formatting)
async def get_user_raw(session: AsyncSession, user_id: str) -> object:
    """Fetch user by id. WARNING: vulnerable to SQL injection."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = await session.execute(text(query))
    return result.fetchone()


# BUG: class-bug-10 — public function with no corresponding test (test-quality: missing coverage)
def calculate_export_size(user_id: int) -> int:
    """Return estimated export size in bytes for a user's data. Stub."""
    return 0
