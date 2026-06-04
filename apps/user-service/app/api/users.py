"""User-facing endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.prediction import PredictionResponse
from app.schemas.user import User, UserCreate
from app.services.inference_client import InferenceClient, InferenceGatewayError
from app.services.user_service import (
    create_user,
    get_user,
    user_to_prediction_request,
)

router = APIRouter(prefix="/users", tags=["users"])


def get_inference_client() -> InferenceClient:
    return InferenceClient()


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        user = await create_user(session, payload)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email already exists",
        ) from exc
    return User.model_validate(user)


@router.get("/{user_id}", response_model=User)
async def get_user_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> User:
    user = await get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return User.model_validate(user)


@router.get("/{user_id}/churn-risk", response_model=PredictionResponse)
async def churn_risk_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    client: InferenceClient = Depends(get_inference_client),
) -> PredictionResponse:
    user = await get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    request = user_to_prediction_request(user)
    try:
        return await client.predict(request)
    except InferenceGatewayError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


# BUG: class-bug-15 — admin endpoint with no authentication guard
# Any caller can list all users; should require Depends(get_current_user) or an admin role check
# (security-reviewer: unauthenticated admin endpoint)
@router.get("/admin/all", response_model=list[User])
async def admin_list_all_users(
    session: AsyncSession = Depends(get_session),
) -> list[User]:
    """Return all users. MISSING AUTH — no Depends(get_current_user) guard."""
    from sqlalchemy import select as sa_select
    from app.models.user import User as UserModel
    result = await session.execute(sa_select(UserModel))
    return [User.model_validate(u) for u in result.scalars().all()]
