#!/usr/bin/env python3
"""
Authentication and User Identity Service
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.domain.entities.user import User
from app.schemas.user import UserOut
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)
from app.core.config import settings
from app.services.email_service import EmailService


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

    @staticmethod
    def forgot_password(db: Session, email: str) -> Optional[str]:
        """
        Generates a password reset token if the given email belongs to a
        registered (non-guest) account.

        Security note
        -------------
        This method intentionally returns ``None`` instead of raising an
        exception when the email is unknown or belongs to a guest.  The
        caller should **always** respond with a generic 200 message so
        that attackers cannot enumerate registered addresses.

        Args:
            db (Session): Database session
            email (str): Email address submitted by the user

        Returns:
            str: A one-hour reset token (caller must deliver it to the user)
            None: If the email is unknown or belongs to a guest user
        """
        import smtplib

        db_user = db.query(User).filter(User.email == email).first()

        # Silently return if the user does not exist or is a guest.
        # This prevents user-enumeration attacks — the API always returns 200.
        if not db_user or db_user.is_guest:
            logger.info("forgot_password: no registered account for email (not disclosed to caller)")
            return None

        # Generate a cryptographically random token and 1-hour expiry
        reset_token = str(uuid.uuid4())
        expires = datetime.now(timezone.utc) + timedelta(hours=1)

        db_user.reset_password_token = reset_token
        db_user.reset_password_expires = expires
        db.add(db_user)
        db.commit()

        # Build the reset deep-link: beautyassistant://reset-password?token=<uuid>
        # FRONTEND_URL already contains the full path e.g. "beautyassistant://reset-password"
        reset_link = f"{settings.frontend_url}?token={reset_token}"

        # Send the email — log the error but do NOT crash the request
        try:
            EmailService.send_reset_password_email(
                to_email=db_user.email,
                reset_link=reset_link,
            )
        except smtplib.SMTPException:
            # SMTP failure is logged inside EmailService._send().
            # We raise a 500 so the frontend knows to prompt the user to retry.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send reset email. Please try again later.",
            )

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> UserOut:
        """
        Resets a user's password using a valid reset token.
        
        Args:
            db (Session): Database session
            token (str): The reset token
            new_password (str): The new password to set
            
        Returns:
            UserOut: The updated user profile
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        db_user = db.query(User).filter(User.reset_password_token == token).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
            
        # Check if token is expired
        if not db_user.reset_password_expires or db_user.reset_password_expires.tzinfo is None:
            # If naive datetime in DB, convert to aware for comparison
            # Assuming DB stores UTC if naive
            now = datetime.now(timezone.utc)
            expires = db_user.reset_password_expires.replace(tzinfo=timezone.utc) if db_user.reset_password_expires else now
        else:
            now = datetime.now(timezone.utc)
            expires = db_user.reset_password_expires
            
        if now > expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
            
        # Token is valid, update password
        db_user.password_hash = get_password_hash(new_password)
        
        # Clear token fields
        db_user.reset_password_token = None
        db_user.reset_password_expires = None
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserOut.model_validate(db_user)
