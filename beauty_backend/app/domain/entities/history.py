#!/usr/bin/env python3
"""
Recommendation history entities for the Beauty Assistant database.
"""

import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisType(str, enum.Enum):
    """Origin of the recommendation session"""
    SCA_SCAN = "sca_scan"
    MANUAL = "manual"


class RecommendationSession(Base):
    """
    Groups multiple recommendations from a single analysis event.
    """
    __tablename__ = "recommendation_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Using Enum as suggested by the design spec (requires values_callable to match DB names)
    analysis_type = Column(Enum(AnalysisType, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=AnalysisType.SCA_SCAN)
    
    # The season assigned during this session (FK reference until seasons table exists)
    season_id = Column(Integer, nullable=True)
    
    # Reference to the selfie image used for analysis
    image_path = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    items = relationship("RecommendationItem", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RecommendationSession(id={self.id}, user_id={self.user_id}, type={self.analysis_type})>"


class RecommendationItem(Base):
    """
    The specific products recommended in a session.
    """
    __tablename__ = "recommendation_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("recommendation_sessions.id"))
    
    # Reference to the cosmetic product (FK reference until cosmetics table exists)
    cosmetic_id = Column(Integer, nullable=False)
    
    # Whether the user "favorited" this item
    is_saved = Column(Boolean, default=False)

    # Relationships
    session = relationship("RecommendationSession", back_populates="items")

    def __repr__(self):
        return f"<RecommendationItem(id={self.id}, session_id={self.session_id}, cosmetic_id={self.cosmetic_id})>"
