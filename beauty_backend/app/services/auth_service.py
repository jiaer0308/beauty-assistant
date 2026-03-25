#!/usr/bin/env python3
"""
Authentication and User Identity Service
"""

import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.entities.user import User
from app.schemas.user import UserOut
from app.core.security import get_password_hash, verify_password


class AuthService:
    """
    Handles guest identity creation, user registration, and authentication.
    """
    
    @staticmethod
    def create_guest_user(db: Session) -> UserOut:
        """
        Generates a unique guest token and creates a new guest user in the database.
        
        Args:
            db (Session): Database session
            
        Returns:
            UserOut: The newly created guest user
        """
        guest_token = str(uuid.uuid4())
        
        db_user = User(
            guest_token=guest_token,
            is_guest=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserOut.model_validate(db_user)

    @staticmethod
    def register_user(db: Session, email: str, password: str, guest_token: str) -> UserOut:
        """
        Upgrades a guest user to a registered user by adding email and password.
        
        Args:
            db (Session): Database session
            email (str): User's email address
            password (str): User's plain-text password
            guest_token (str): The token of the guest session to upgrade
            
        Returns:
            UserOut: The updated user profile
            
        Raises:
            HTTPException: If guest not found, already registered, or email taken
        """
        # Find the guest user
        db_user = db.query(User).filter(User.guest_token == guest_token).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Guest session not found"
            )
        
        if not db_user.is_guest:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This session is already registered to an account"
            )
            
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        # Upgrade guest to user
        db_user.email = email
        db_user.password_hash = get_password_hash(password)
        db_user.is_guest = False
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserOut.model_validate(db_user)

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> UserOut:
        """
        Verifies user credentials and returns the user profile.
        
        Args:
            db (Session): Database session
            email (str): User's email
            password (str): User's plain-text password
            
        Returns:
            UserOut: The authenticated user profile
            
        Raises:
            HTTPException: If authentication fails
        """
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not verify_password(password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return UserOut.model_validate(db_user)
