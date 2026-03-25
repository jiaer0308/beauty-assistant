#!/usr/bin/env python3
"""
Authentication and User Identity API Endpoints
"""

import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserOut, UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.core.security import create_access_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/guest",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a guest user identity",
    description="Generates a unique guest token and returns a new guest user ID."
)
def create_guest_user(db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/guest
    
    Returns:
        UserOut: The newly created guest user
    """
    return AuthService.create_guest_user(db)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Register a user account (upgrade guest)",
    description="Upgrades a guest session to a permanent account with email and password."
)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/register
    
    Args:
        user_in (UserCreate): Registration data (must include email, password, and guest_token)
        
    Returns:
        UserResponse: The upgraded user profile and access token
    """
    if not user_in.email or not user_in.password or not user_in.guest_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, password, and guest_token are required for registration"
        )
        
    user = AuthService.register_user(
        db, 
        email=user_in.email, 
        password=user_in.password, 
        guest_token=user_in.guest_token
    )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return UserResponse(
        user=user,
        token=Token(access_token=access_token, token_type="bearer")
    )


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticates user with email and password, returning user profile and access token."
)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/login
    
    Args:
        credentials (UserLogin): User's login credentials
        
    Returns:
        UserResponse: The user profile and access token
    """
    user = AuthService.authenticate_user(
        db, 
        email=credentials.email, 
        password=credentials.password
    )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return UserResponse(
        user=user,
        token=Token(access_token=access_token, token_type="bearer")
    )
