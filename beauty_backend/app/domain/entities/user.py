#!/usr/bin/env python3
"""
User entity model for the Beauty Assistant database.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.core.database import Base

user_favorite_cosmetics = Table(
    'user_favorite_cosmetics', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('cosmetic_id', Integer, ForeignKey('cosmetic_products.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


class User(Base):
    """
    User model representing both guest and registered identities.
    
    This follows the 'Identity Bridge' pattern, allowing guests to later
    register with an email/password without losing history.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    guest_token = Column(String(255), unique=True, index=True, nullable=True)
    
    # Password reset fields
    reset_password_token = Column(String(255), unique=True, index=True, nullable=True)
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)
    
    # ID from the 'seasons' table in the knowledge base
    # For now, this is just an integer reference until the seasons model is implemented
    current_season_id = Column(Integer, nullable=True)
    
    is_guest = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sessions = relationship("RecommendationSession", back_populates="user", cascade="all, delete-orphan")
    favorite_cosmetics = relationship("CosmeticProduct", secondary=user_favorite_cosmetics, backref="favorited_by")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', is_guest={self.is_guest})>"
