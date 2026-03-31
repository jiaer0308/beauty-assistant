import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.database import Base
from app.domain.entities.knowledge_base import (
    Season, Color, SeasonColor, CategoryType, Brand, Category, CosmeticProduct, CosmeticSeasonMapping
)
from app.services.recommendation_mapper import RecommendationMapper

# Set up an in-memory SQLite database for testing
@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Seed data
    winter = Season(name="dark_winter", description="Dark Winter")
    db.add(winter)
    db.commit()
    
    red = Color(name="True Red", hex_code="#C8102E")
    db.add(red)
    db.commit()
    
    sc = SeasonColor(season_id=winter.id, color_id=red.id, category_type=CategoryType.BEST)
    db.add(sc)
    
    brand = Brand(name="MAC")
    db.add(brand)
    db.commit()
    
    cat = Category(name="Lipstick")
    db.add(cat)
    db.commit()
    
    prod = CosmeticProduct(
        brand_id=brand.id,
        category_id=cat.id,
        product_name="Lipstick",
        shade_name="Ruby Woo",
        hex_code="#9B111E",
        is_active=True
    )
    db.add(prod)
    db.commit()
    
    mapping = CosmeticSeasonMapping(season_id=winter.id, cosmetic_id=prod.id)
    db.add(mapping)
    db.commit()
    
    yield db
    db.close()

def test_get_recommendations_basic(db_session: Session):
    mapper = RecommendationMapper()
    recs = mapper.get_recommendations("dark_winter", db_session)
    
    assert "best_colors" in recs
    assert recs["best_colors"][0]["name"] == "True Red"
    assert recs["best_colors"][0]["hex"] == "#C8102E"
    
    assert "cosmetics" in recs
    assert len(recs["cosmetics"]) == 1
    assert recs["cosmetics"][0]["brand"] == "MAC"
    assert recs["cosmetics"][0]["category"] == "Lipstick"
    assert recs["cosmetics"][0]["shade"] == "Ruby Woo"
    assert recs["cosmetics"][0]["hex"] == "#9B111E"

def test_get_recommendations_invalid_season(db_session: Session):
    mapper = RecommendationMapper()
    with pytest.raises(ValueError, match="No recommendations found for season 'invalid_season'"):
        mapper.get_recommendations("invalid_season", db_session)

def test_get_recommendations_category_limit(db_session: Session):
    """
    Verify that if there are >5 products in a category, only 5 are returned.
    """
    mapper = RecommendationMapper()
    
    # 1. Setup a season
    autumn = Season(name="soft_autumn", description="Soft Autumn")
    db_session.add(autumn)
    db_session.commit()
    
    # 2. Setup a category and brand
    cat = Category(name="Foundation")
    brand = Brand(name="The Ordinary")
    db_session.add_all([cat, brand])
    db_session.commit()
    
    # 3. Create 7 products in the same category
    for i in range(7):
        prod = CosmeticProduct(
            brand_id=brand.id,
            category_id=cat.id,
            product_name=f"Foundation {i}",
            shade_name=f"Shade {i}",
            hex_code="#FFFFFF",
            is_active=True
        )
        db_session.add(prod)
        db_session.commit()
        
        mapping = CosmeticSeasonMapping(season_id=autumn.id, cosmetic_id=prod.id)
        db_session.add(mapping)
        db_session.commit()
        
    # 4. Fetch recommendations
    recs = mapper.get_recommendations("soft_autumn", db_session)
    
    # 5. Assert that only 5 are returned for the category
    foundations = [p for p in recs["cosmetics"] if p["category"] == "Foundation"]
    assert len(foundations) == 5
    assert len(recs["cosmetics"]) == 5

def test_get_recommendations_quiz_filtering_coverage(db_session: Session):
    """
    Verify that foundation_coverage='Sheer/Light' filters out 'Foundation'
    category but keeps 'BB/CC Cream'.
    """
    mapper = RecommendationMapper()
    season_name = "light_summer"
    season = Season(name=season_name)
    db_session.add(season)
    db_session.commit()
    
    brand = Brand(name="Test Brand")
    db_session.add(brand)
    
    cat_foundation = Category(name="Foundation")
    cat_bb = Category(name="BB/CC Cream")
    db_session.add_all([cat_foundation, cat_bb])
    db_session.commit()
    
    # Add a foundation
    prod1 = CosmeticProduct(
        brand_id=brand.id, category_id=cat_foundation.id,
        product_name="Heavy Foundation", shade_name="Fair", is_active=True
    )
    # Add a BB Cream
    prod2 = CosmeticProduct(
        brand_id=brand.id, category_id=cat_bb.id,
        product_name="Light BB Cream", shade_name="Fair", is_active=True
    )
    db_session.add_all([prod1, prod2])
    db_session.commit()
    
    db_session.add_all([
        CosmeticSeasonMapping(season_id=season.id, cosmetic_id=prod1.id),
        CosmeticSeasonMapping(season_id=season.id, cosmetic_id=prod2.id)
    ])
    db_session.commit()
    
    # 1. No quiz data - should get both
    recs_no_quiz = mapper.get_recommendations(season_name, db_session)
    assert len(recs_no_quiz["cosmetics"]) == 2
    
    # 2. Quiz data: Sheer/Light - should only get BB Cream
    quiz_data = {"foundation_coverage": "Sheer/Light"}
    recs_quiz = mapper.get_recommendations(season_name, db_session, quiz_data=quiz_data)
    
    categories = [p["category"] for p in recs_quiz["cosmetics"]]
    assert "BB/CC Cream" in categories
    assert "Foundation" not in categories
    assert len(recs_quiz["cosmetics"]) == 1

def test_get_recommendations_quiz_filtering_skin_type(db_session: Session):
    """
    Verify that skin_type='Oily' filters out categories containing 'Cream'.
    """
    mapper = RecommendationMapper()
    season_name = "bright_spring"
    season = Season(name=season_name)
    db_session.add(season)
    db_session.commit()
    
    brand = Brand(name="Test Brand")
    db_session.add(brand)
    
    cat_cream = Category(name="Cream Blush")
    cat_powder = Category(name="Powder Blush")
    db_session.add_all([cat_cream, cat_powder])
    db_session.commit()
    
    prod1 = CosmeticProduct(
        brand_id=brand.id, category_id=cat_cream.id,
        product_name="Creamy Pink", shade_name="Pink", is_active=True
    )
    prod2 = CosmeticProduct(
        brand_id=brand.id, category_id=cat_powder.id,
        product_name="Powder Pink", shade_name="Pink", is_active=True
    )
    db_session.add_all([prod1, prod2])
    db_session.commit()
    
    db_session.add_all([
        CosmeticSeasonMapping(season_id=season.id, cosmetic_id=prod1.id),
        CosmeticSeasonMapping(season_id=season.id, cosmetic_id=prod2.id)
    ])
    db_session.commit()
    
    # 1. No quiz data - should get both
    recs_no_quiz = mapper.get_recommendations(season_name, db_session)
    assert len(recs_no_quiz["cosmetics"]) == 2
    
    # 2. Quiz data: Oily - should only get Powder Blush
    quiz_data = {"skin_type": "Oily"}
    recs_quiz = mapper.get_recommendations(season_name, db_session, quiz_data=quiz_data)
    
    categories = [p["category"] for p in recs_quiz["cosmetics"]]
    assert "Powder Blush" in categories
    assert "Cream Blush" not in categories
    assert len(recs_quiz["cosmetics"]) == 1
