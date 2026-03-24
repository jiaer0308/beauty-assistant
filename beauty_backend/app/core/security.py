#!/usr/bin/env python3
"""
Security utilities for password hashing and JWT token management.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt hash of the given password.
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def get_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token, returning its payload.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None
