#!/usr/bin/env python3
"""
Authentication and User Identity API Endpoints
"""

import logging
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserOut, UserCreate, UserLogin, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from app.api.deps import get_current_user
from app.domain.entities.user import User

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
def login_user(credentials: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/login
    
    Args:
        credentials (OAuth2PasswordRequestForm): User's login credentials (username/password)
        
    Returns:
        UserResponse: The user profile and access token
    """
    user = AuthService.authenticate_user(
        db, 
        email=credentials.username,
        password=credentials.password
    )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return UserResponse(
        user=user,
        token=Token(access_token=access_token, token_type="bearer")
    )


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request a password reset token",
    description="Generates a password reset token for a registered user. In a real app, this would send an email."
)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/forgot-password
    
    Args:
        request (ForgotPasswordRequest): Contains the user's email
        
    Returns:
        dict: A dictionary containing the reset token (for testing purposes)
    """
    token = AuthService.forgot_password(db, email=request.email)
    
    # Normally we would just return {"message": "If the email exists, a reset link has been sent"}
    # But for testing without an email service, we return the token directly.
    return {
        "message": "Password reset token generated", 
        "reset_token": token
    }


@router.post(
    "/reset-password",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Reset a user's password",
    description="Resets a user's password using a valid reset token."
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/reset-password
    
    Args:
        request (ResetPasswordRequest): Contains the token and new password.
        
    Returns:
        UserOut: The updated user profile.
    """
    return AuthService.reset_password(
        db, 
        token=request.token, 
        new_password=request.new_password
    )


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile (Verify Token)",
    description="Returns the currently authenticated user based on the bearer token."
)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    GET /api/v1/auth/me
    
    Args:
        current_user (User): The user resolved from the bearer token.
        
    Returns:
        UserOut: The current user's profile.
    """
    return current_user

