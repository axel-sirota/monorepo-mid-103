"""Pydantic v2 models for the User API surface."""
# BUG: class-bug-7 (lib-extractor): User shape duplicated — also defined in
# api-gateway UserDto.java and notification-service internal/model/user.go.
# TODO: deduplicate
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=200)
    engagement_score: float = Field(default=0.5, ge=0.0, le=1.0)
    days_since_login: int = Field(default=0, ge=0)
    sessions_last_30d: int = Field(default=0, ge=0)
    support_tickets_last_90d: int = Field(default=0, ge=0)


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)
    email: EmailStr
    full_name: str | None = None
    created_at: datetime
    engagement_score: float = Field(ge=0.0, le=1.0)
    days_since_login: int = Field(ge=0)
    sessions_last_30d: int = Field(ge=0)
    support_tickets_last_90d: int = Field(ge=0)
    # NOTE: export_url intentionally absent — present in contracts/schemas/user.json
    # This is BUG class-bug-4 (contract-cop): schema/Pydantic model drift
