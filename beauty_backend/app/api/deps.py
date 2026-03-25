#!/usr/bin/env python3
"""
FastAPI Dependencies

Provides shared dependencies for the API layer via FastAPI's
Depends() injection system.
"""

from typing import Annotated, Optional

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.domain.entities.user import User
from app.services.sca_workflow_service import SCAWorkflowService


# Token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    auto_error=False  # Allow guest access without token where appropriate
)


def get_sca_service(request: Request) -> SCAWorkflowService:
    """
    Retrieve the SCAWorkflowService singleton stored on app.state.

    The service is initialised once during application startup (see main.py
    lifespan) so that the heavy ML models are loaded only once, not per
    request.
    """
    return request.app.state.sca_service


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """
    Dependency that extracts the user identity from either a JWT token 
    or an X-Guest-Token header.
    
    Returns the User model (can be a guest or registered user).
    Raises 401 Unauthorized if no valid identity is found.
    """
    # 1. Try JWT Token First (Registered Users)
    if token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            user_id_str: str = payload.get("sub")
            if user_id_str:
                user = db.query(User).filter(User.id == int(user_id_str)).first()
                if user:
                    return user
        except (JWTError, ValueError):
            pass

    # 2. Try X-Guest-Token Header (Anonymous Flow)
    guest_token = request.headers.get("X-Guest-Token")
    if guest_token:
        user = db.query(User).filter(User.guest_token == guest_token).first()
        if user:
            return user
            
    # 3. No valid identity found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required (Valid JWT or X-Guest-Token expected)",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Convenience type aliases for use in endpoint signatures
SCAServiceDep = Annotated[SCAWorkflowService, Depends(get_sca_service)]
DBDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
