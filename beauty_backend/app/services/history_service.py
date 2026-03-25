#!/usr/bin/env python3
"""
Recommendation History Service

Handles persistence and retrieval of analysis events and 
the products recommended during those events.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.entities.history import RecommendationSession, RecommendationItem, AnalysisType
from app.schemas.history import RecommendationSessionOut, RecommendationSessionDetailOut


class HistoryService:
    """
    Handles saving and retrieving recommendation sessions for users.
    """

    @staticmethod
    def save_session(
        db: Session, 
        user_id: int, 
        analysis_type: str, 
        season_id: int, 
        cosmetic_ids: List[int], 
        image_path: Optional[str] = None
    ) -> RecommendationSessionDetailOut:
        """
        Saves a new recommendation session and its associated products.
        
        Args:
            db (Session): Database session
            user_id (int): ID of the user
            analysis_type (str): Origin of the recommendation ('sca_scan' or 'manual')
            season_id (int): The season ID assigned
            cosmetic_ids (List[int]): List of recommended product IDs
            image_path (str, optional): Path to the selfie used
            
        Returns:
            RecommendationSessionDetailOut: The saved session with all items
        """
        # Convert string analysis_type to Enum
        try:
            # Map common strings to enum values if they don't match exactly
            clean_type = analysis_type.lower().replace(" ", "_")
            enum_type = AnalysisType(clean_type)
        except ValueError:
            # Fallback to SCA_SCAN if invalid type provided
            enum_type = AnalysisType.SCA_SCAN

        # 1. Create the session header
        db_session = RecommendationSession(
            user_id=user_id,
            analysis_type=enum_type,
            season_id=season_id,
            image_path=image_path
        )
        db.add(db_session)
        db.flush()  # Ensure db_session.id is populated

        # 2. Create individual items
        for cosmetic_id in cosmetic_ids:
            item = RecommendationItem(
                session_id=db_session.id,
                cosmetic_id=cosmetic_id
            )
            db.add(item)

        db.commit()
        db.refresh(db_session)
        
        return RecommendationSessionDetailOut.model_validate(db_session)

    @staticmethod
    def get_user_history(db: Session, user_id: int) -> List[RecommendationSessionOut]:
        """
        Retrieves all recommendation sessions for a user, newest first.
        
        Args:
            db (Session): Database session
            user_id (int): User ID to fetch history for
            
        Returns:
            List[RecommendationSessionOut]: List of session summaries
        """
        sessions = db.query(RecommendationSession).filter(
            RecommendationSession.user_id == user_id
        ).order_by(RecommendationSession.created_at.desc()).all()
        
        return [RecommendationSessionOut.model_validate(s) for s in sessions]

    @staticmethod
    def get_session_detail(db: Session, session_id: int) -> RecommendationSessionDetailOut:
        """
        Retrieves full details (including items) for a specific session.
        
        Args:
            db (Session): Database session
            session_id (int): The ID of the session to retrieve
            
        Returns:
            RecommendationSessionDetailOut: The full session details
            
        Raises:
            HTTPException: If session is not found
        """
        db_session = db.query(RecommendationSession).filter(
            RecommendationSession.id == session_id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation session {session_id} not found"
            )
            
        return RecommendationSessionDetailOut.model_validate(db_session)
