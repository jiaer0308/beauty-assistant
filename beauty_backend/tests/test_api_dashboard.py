#!/usr/bin/env python3
"""
Dashboard API Integration Tests

Tests the data aggregation endpoint `/api/v1/dashboard`
using an in-memory SQLite database for fast unit testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.domain.entities.user import User
from app.domain.entities.history import RecommendationSession, RecommendationItem
from app.domain.entities.knowledge_base import Season, CosmeticProduct, Brand, Category


# ---------------------------------------------------------------------------
# Setup In-Memory DB
# ---------------------------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(name="db")
def db_fixture():
    # Setup
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Needs a mock user
    user = User(id=1, email="dashboard_test@example.com", is_guest=True, guest_token="fake_guest_token")
    db.add(user)
    db.commit()

    yield db
    
    # Teardown
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def client_fixture():
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetDashboard:

    def test_empty_dashboard(self, client, db):
        """User with no history should receive a graceful empty response."""
        response = client.get("/api/v1/dashboard?guest_token=fake_guest_token")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["result"] is None
        assert data["recommended_products"] == []

    def test_invalid_guest_token(self, client, db):
        """Invalid guest token should return 404."""
        response = client.get("/api/v1/dashboard?guest_token=invalid_token")
        assert response.status_code == 404

    def test_populated_dashboard(self, client, db):
        """User with history should receive their latest season & products."""
        
        # 1. Setup static baseline DB entities
        season = Season(id=10, name="Deep Autumn")
        brand = Brand(id=5, name="NARS")
        category = Category(id=1, name="Blush")
        product = CosmeticProduct(
            id=100, 
            brand_id=5, 
            category_id=1,
            product_name="Liquid Blush", 
            shade_name="Orgasm", 
            image_url="https://example.com/orgasm.png"
        )
        db.add_all([season, brand, category, product])
        db.commit()

        # 2. Add an older session
        old_session = (RecommendationSession(id=1, user_id=1, season_id=10))
        db.add(old_session)
        db.commit()
        db.add(RecommendationItem(session_id=1, cosmetic_id=100))

        # 3. Add a newer session (which should be the returned one)
        new_session = (RecommendationSession(id=2, user_id=1, season_id=10))
        db.add(new_session)
        db.commit()
        db.add(RecommendationItem(session_id=2, cosmetic_id=100))
        db.commit()

        # 4. Perform the GET request
        response = client.get("/api/v1/dashboard?guest_token=fake_guest_token")
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["result"]["display_name"] == "Deep Autumn"
        assert data["result"]["season"] == "deep_autumn"
        
        products = data["recommended_products"]
        assert len(products) == 1
        assert products[0]["brand"] == "NARS"
        assert products[0]["name"] == "Liquid Blush in Orgasm"
        assert products[0]["image_url"] == "https://example.com/orgasm.png"
