#!/usr/bin/env python3
"""
Tests for Recommendation History Service

Verifies the persistence and retrieval of analysis sessions
and product recommendations.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException

from app.core.database import Base
from app.domain.entities.user import User
from app.domain.entities.history import RecommendationSession, RecommendationItem
from app.services.history_service import HistoryService


# Setup an in-memory SQLite database for fast unit testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="db")
def db_fixture():
    """Provides a clean, migrated database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="test_user")
def user_fixture(db):
    """Provides a test user in the database."""
    user = User(
        email="test_history@example.com",
        is_guest=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestHistoryPersistence:
    """Unit tests for HistoryService data operations."""

    def test_save_new_session(self, db, test_user):
        """Verify that a session and its items are correctly saved."""
        # Arrange
        analysis_type = "sca_scan"
        season_id = 1
        cosmetic_ids = [101, 102, 103]
        image_path = "uploads/faces/test.jpg"

        # Act
        result = HistoryService.save_session(
            db, 
            user_id=test_user.id, 
            analysis_type=analysis_type, 
            season_id=season_id, 
            cosmetic_ids=cosmetic_ids, 
            image_path=image_path
        )

        # Assert: Service return value
        assert result.user_id == test_user.id
        assert result.analysis_type == analysis_type
        assert result.season_id == season_id
        assert len(result.items) == 3
        assert result.items[0].cosmetic_id == 101

        # Assert: Database state
        db_session = db.query(RecommendationSession).filter_by(id=result.id).one()
        assert db_session.user_id == test_user.id
        assert len(db_session.items) == 3
        assert db_session.items[1].cosmetic_id == 102

    def test_retrieve_user_history_sorting(self, db, test_user):
        """Verify that history is returned with the newest sessions first."""
        # Arrange: Save two sessions at slightly different times
        HistoryService.save_session(db, test_user.id, "sca_scan", 1, [1])
        HistoryService.save_session(db, test_user.id, "manual", 2, [2])

        # Act
        history = HistoryService.get_user_history(db, test_user.id)

        # Assert: Newest first (manual was second)
        assert len(history) == 2
        assert history[0].analysis_type == "manual"
        assert history[1].analysis_type == "sca_scan"

    def test_get_session_details(self, db, test_user):
        """Verify that detailed session data includes all items."""
        # Arrange
        saved = HistoryService.save_session(db, test_user.id, "sca_scan", 1, [500])

        # Act
        detail = HistoryService.get_session_detail(db, saved.id)

        # Assert
        assert detail.id == saved.id
        assert len(detail.items) == 1
        assert detail.items[0].cosmetic_id == 500

    def test_get_missing_session_raises_404(self, db):
        """Verify that non-existent sessions trigger a 404 error."""
        with pytest.raises(HTTPException) as exc:
            HistoryService.get_session_detail(db, 99999)
        
        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    def test_analysis_type_normalization(self, db, test_user):
        """Verify that variations of analysis type strings are handled."""
        # Act
        res1 = HistoryService.save_session(db, test_user.id, "SCA SCAN", 1, [1])
        res2 = HistoryService.save_session(db, test_user.id, "manual_override", 1, [1]) # invalid type

        # Assert
        assert res1.analysis_type == "sca_scan"
        assert res2.analysis_type == "sca_scan"  # Fallback logic in service
