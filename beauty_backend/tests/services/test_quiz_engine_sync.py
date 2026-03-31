import pytest
from app.schemas.sca import QuizData
from app.services.quiz_engine import QuizEngine, ALL_SEASONS, _WARM_SEASONS, _COOL_SEASONS

def test_quiz_engine_sync_logic():
    engine = QuizEngine()
    
    # Test case: Strong warm signals
    quiz_warm = QuizData(
        wrist_vein="Green or Olive",
        jewelry="Yellow Gold",
        sun_reaction="Tan easily, rarely burn",
        hair_color="Warm Brown"
    )
    
    image_scores = {s: 0.5 for s in ALL_SEASONS}
    fused = engine.compute_quiz_adjustments(quiz_warm, image_scores)
    
    # Warm seasons should be higher than cool seasons
    warm_avg = sum(fused[s] for s in _WARM_SEASONS) / len(_WARM_SEASONS)
    cool_avg = sum(fused[s] for s in _COOL_SEASONS) / len(_COOL_SEASONS)
    
    assert warm_avg > cool_avg

def test_quiz_engine_sync_cool_logic():
    engine = QuizEngine()
    
    # Test case: Strong cool signals
    quiz_cool = QuizData(
        wrist_vein="Blue or Purple",
        jewelry="Silver / White Gold",
        sun_reaction="Burn easily, rarely tan",
        hair_color="Ashy Blonde"
    )
    
    image_scores = {s: 0.5 for s in ALL_SEASONS}
    fused = engine.compute_quiz_adjustments(quiz_cool, image_scores)
    
    # Cool seasons should be higher than warm seasons
    warm_avg = sum(fused[s] for s in _WARM_SEASONS) / len(_WARM_SEASONS)
    cool_avg = sum(fused[s] for s in _COOL_SEASONS) / len(_COOL_SEASONS)
    
    assert cool_avg > warm_avg
