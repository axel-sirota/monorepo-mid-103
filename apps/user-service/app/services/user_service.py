"""Pure business logic for User CRUD and feature mapping."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User as UserModel
from app.schemas.prediction import PredictionRequest
from app.schemas.user import UserCreate


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
