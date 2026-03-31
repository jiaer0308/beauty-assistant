#!/usr/bin/env python3
"""
Recommendation History API Endpoints

Provides access to past Seasonal Colour Analysis results and
their associated product recommendations.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, DBDep
from app.schemas.history import RecommendationSessionOut, RecommendationSessionDetailOut
from app.services.history_service import HistoryService

router = APIRouter()


@router.get(
    "/",
    response_model=List[RecommendationSessionOut],
    summary="Get user recommendation history",
    description="Retrieves a list of all past analysis sessions for the authenticated user, sorted by date (newest first)."
)
def get_history(
    current_user: CurrentUserDep,
    db: DBDep
):
    """
    GET /api/v1/history/
    
    Returns:
        List[RecommendationSessionOut]: List of session summaries
    """
    return HistoryService.get_user_history(db, current_user.id)


@router.get(
    "/{session_id}",
    response_model=RecommendationSessionDetailOut,
    summary="Get recommendation session details",
    description="Retrieves the full details of a specific analysis session, including the list of recommended products."
)
def get_session_detail(
    session_id: int,
    current_user: CurrentUserDep,
    db: DBDep
):
    """
    GET /api/v1/history/{session_id}
    
    Args:
        session_id (int): The ID of the session to retrieve
        
    Returns:
        RecommendationSessionDetailOut: The full session details with items
        
    Raises:
        HTTPException 403: If the session does not belong to the user
        HTTPException 404: If the session does not exist
    """
    # 1. Fetch the session details via service
    # (The service raises 404 if not found)
    session_detail = HistoryService.get_session_detail(db, session_id)
    
    # 2. Security Check: Ensure the session belongs to the current user
    if session_detail.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this recommendation session history."
        )
        
    return session_detail

@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recommendation session",
    description="Deletes a specific analysis session and its associated products."
)
def delete_session(
    session_id: int,
    current_user: CurrentUserDep,
    db: DBDep
):
    """
    DELETE /api/v1/history/{session_id}
    
    Args:
        session_id (int): The ID of the session to delete
        
    Raises:
        HTTPException 403: If the session does not belong to the user
        HTTPException 404: If the session does not exist
    """
    # 1. Fetch the session details to verify ownership
    session_detail = HistoryService.get_session_detail(db, session_id)
    
    # 2. Security Check: Ensure the session belongs to the current user
    if session_detail.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this recommendation session."
        )
        
    # 3. Delete the session
    HistoryService.archive_session(db, session_id)
    return None
