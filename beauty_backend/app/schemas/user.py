#!/usr/bin/env python3
"""
User and Authentication Schemas (Pydantic V2)

These models define the JSON contract for user management,
authentication, and guest identity management.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Common fields for user and guest identities."""
    email: str | None = Field(
        default=None, 
        examples=["user@example.com"],
        description="User email (NULL for guest sessions)"
    )
    guest_token: str | None = Field(
        default=None, 
        description="Unique UUID for anonymous tracking"
    )
    current_season_id: int | None = Field(
        default=None, 
        description="The user's last SCA result ID (FK to seasons.id)"
    )
    is_guest: bool = Field(
        default=True, 
        description="Identifies anonymous vs registered"
    )


class UserCreate(UserBase):
    """
    For creating new users or guest sessions.
    
    If password is provided, creates a registered user.
    If only guest_token is provided, initializes a guest.
    """
    password: str | None = Field(
        default=None, 
        min_length=8, 
        description="User password (required for registration)"
    )


class UserUpdate(BaseModel):
    """For updating user profile information."""
    email: str | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8)
    current_season_id: int | None = Field(default=None)


class UserOut(UserBase):
    """
    For returning user information.
    
    Excludes sensitive fields like password_hash.
    """
    id: int = Field(..., examples=[1])
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Credentials for user login."""
    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    """JWT response structure returned by login/register endpoints."""
    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field(default="bearer", description="Token type, usually 'bearer'")


class UserResponse(BaseModel):
    """Combined user profile and authentication token."""
    user: UserOut
    token: Token


class TokenData(BaseModel):
    """Internal JWT payload representation for user identification."""
    user_id: int | None = Field(default=None, description="Decoded user ID from the token")
