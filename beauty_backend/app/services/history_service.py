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
from app.domain.entities.knowledge_base import CosmeticProduct, Season
from app.schemas.history import RecommendationSessionOut, RecommendationSessionDetailOut
from app.schemas.cosmetic import CosmeticSessionItem


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
        image_path: Optional[str] = None,
    ) -> RecommendationSessionDetailOut:
        """
        Saves a new recommendation session and its associated products.
        
        Args:
            db (Session): Database session
            user_id (int): ID of the user
            analysis_type (str): Origin of the recommendation ('sca_scan' or 'manual')
            season_id (int): The season ID assigned (FK to seasons.id)
            cosmetic_ids (List[int]): List of recommended product IDs
            image_path (str, optional): Path to the selfie used
            
        Returns:
            RecommendationSessionDetailOut: The saved session with all items
        """
        # Convert string analysis_type to Enum
        try:
            clean_type = analysis_type.lower().replace(" ", "_")
            enum_type = AnalysisType(clean_type)
        except ValueError:
            enum_type = AnalysisType.SCA_SCAN

        # 1. Create the session header
        db_session = RecommendationSession(
            user_id=user_id,
            analysis_type=enum_type,
            season_id=season_id,
            image_path=image_path,
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
        
        # Fetch the season name via JOIN for the response
        season = db.query(Season).filter(Season.id == season_id).first()
        season_name = season.name if season else None

        return HistoryService._build_session_detail(db, db_session, season_name)

    @staticmethod
    def get_user_history(db: Session, user_id: int) -> List[RecommendationSessionOut]:
        """
        Retrieves all recommendation sessions for a user, newest first.
        Joins the seasons table to include the human-readable season name.
        
        Args:
            db (Session): Database session
            user_id (int): User ID to fetch history for
            
        Returns:
            List[RecommendationSessionOut]: List of session summaries with season_name
        """
        # LEFT OUTER JOIN seasons so nulls are tolerated
        results = (
            db.query(RecommendationSession, Season.name.label("season_name"))
            .outerjoin(Season, RecommendationSession.season_id == Season.id)
            .filter(
                RecommendationSession.user_id == user_id,
                RecommendationSession.is_archived == False,
            )
            .order_by(RecommendationSession.created_at.desc())
            .all()
        )

        output: List[RecommendationSessionOut] = []
        for session_row, season_name in results:
            # model_validate reads all columns from the ORM object
            base = RecommendationSessionOut.model_validate(session_row)
            # Inject season_name (not a column on the ORM model — comes from JOIN)
            base_dict = base.model_dump()
            base_dict["season_name"] = season_name
            # Inject item count from the relationship
            base_dict["item_count"] = len(session_row.items)
            output.append(RecommendationSessionOut(**base_dict))

        return output

    @staticmethod
    def get_session_detail(db: Session, session_id: int) -> RecommendationSessionDetailOut:
        """
        Retrieves full session details including enriched cosmetic product items.
        Joins the seasons table to include the human-readable season name.
        
        Args:
            db (Session): Database session
            session_id (int): The ID of the session to retrieve
            
        Returns:
            RecommendationSessionDetailOut: Full session with enriched product items
            
        Raises:
            HTTPException 404: If session is not found
        """
        result = (
            db.query(RecommendationSession, Season.name.label("season_name"))
            .outerjoin(Season, RecommendationSession.season_id == Season.id)
            .filter(
                RecommendationSession.id == session_id,
                RecommendationSession.is_archived == False,
            )
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation session {session_id} not found"
            )

        db_session, season_name = result
        return HistoryService._build_session_detail(db, db_session, season_name)

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _build_session_detail(
        db: Session,
        db_session: RecommendationSession,
        season_name: Optional[str],
    ) -> RecommendationSessionDetailOut:
        """
        Builds a RecommendationSessionDetailOut by enriching each item with
        cosmetic product data (brand, name, shade, image_url, hex_code).

        Uses a single batch IN query instead of one query per item to
        avoid the N+1 anti-pattern.
        """
        from sqlalchemy.orm import joinedload as _joinedload
        from app.domain.entities.knowledge_base import Brand

        # Batch-load all referenced products in a single query
        cosmetic_ids = [item.cosmetic_id for item in db_session.items]
        products = (
            db.query(CosmeticProduct)
            .options(_joinedload(CosmeticProduct.brand))
            .filter(
                CosmeticProduct.id.in_(cosmetic_ids),
                CosmeticProduct.is_active == True,
            )
            .all()
        )
        product_map: dict = {p.id: p for p in products}

        enriched_items: List[CosmeticSessionItem] = []
        for item in db_session.items:
            product = product_map.get(item.cosmetic_id)
            if product is None:
                continue  # Skip orphaned items gracefully

            brand_name = product.brand.name if product.brand else "Unknown"
            enriched_items.append(
                CosmeticSessionItem(
                    id=product.id,
                    product_name=product.product_name,
                    shade_name=product.shade_name,
                    brand_name=brand_name,
                    category_id=product.category_id,
                    hex_code=product.hex_code,
                    image_url=product.image_url,
                )
            )

        # Build base dict from ORM object then inject JOIN fields
        base = RecommendationSessionOut.model_validate(db_session)
        base_dict = base.model_dump()
        base_dict["season_name"] = season_name
        base_dict["item_count"] = len(db_session.items)
        base_dict["items"] = enriched_items

        return RecommendationSessionDetailOut(**base_dict)


    @staticmethod
    def archive_session(db: Session, session_id: int) -> bool:
        """
        Soft-deletes a specific recommendation session by marking it as archived.
        
        Args:
            db (Session): Database session
            session_id (int): The ID of the session to archive
            
        Returns:
            bool: True if archived successfully
            
        Raises:
            HTTPException 404: If session is not found
        """
        db_session = db.query(RecommendationSession).filter(
            RecommendationSession.id == session_id,
            RecommendationSession.is_archived == False
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation session {session_id} not found"
            )
            
        db_session.is_archived = True
        db.commit()
        return True
