#!/usr/bin/env python3
"""
Integration Tests – SCA API Endpoints

Uses FastAPI's TestClient with dependency_overrides to mock the heavy
SCAWorkflowService so tests run in milliseconds without loading ML models.
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# ── App under test ────────────────────────────────────────────────────────
from app.main import app
from app.api.deps import get_sca_service
from app.domain.entities.season_result import SeasonResult
from app.domain.value_objects.seasonal_season import SeasonalSeason


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jpeg_bytes(width: int = 200, height: int = 200) -> bytes:
    """Create a minimal valid JPEG image in memory."""
    buf = BytesIO()
    img = Image.new("RGB", (width, height), color=(200, 160, 120))
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _make_png_bytes() -> bytes:
    """Create a minimal valid PNG image in memory."""
    buf = BytesIO()
    img = Image.new("RGB", (100, 100), color=(180, 140, 100))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _mock_season_result() -> MagicMock:
    """Build a realistic SeasonResult mock that matches all entity validation."""
    result = MagicMock(spec=SeasonResult)
    result.season = SeasonalSeason.SOFT_AUTUMN
    result.confidence = 0.82
    result.display_name = "Soft Autumn"
    result.contrast_score = 24.5
    result.skin_temperature = "warm"
    result.skin_color = [210, 168, 130]
    result.hair_color = [80, 55, 40]
    result.eye_color = [100, 80, 60]
    result.processing_time_ms = 850
    result.lighting_quality = "good"
    result.rotation_angle = 2.3
    result.timestamp = datetime(2026, 3, 3, 1, 0, 0)
    # ── NEW fields ──────────────────────────────────────────────────────────
    result.quiz_influence = 0.18
    result.recommendations = {
        "best_colors": [
            {"name": "Warm Taupe",   "hex": "#937166"},
            {"name": "Muted Sage",   "hex": "#89A07A"},
            {"name": "Dusty Peach",  "hex": "#D9A98F"},
            {"name": "Caramel",      "hex": "#C68642"},
            {"name": "Soft Teal",    "hex": "#7AA4A4"},
        ],
        "neutral_colors": [
            {"name": "Warm Sand",    "hex": "#C2A882"},
            {"name": "Mocha",        "hex": "#8B6B61"},
            {"name": "Dusty Coral",  "hex": "#CC8E7A"},
            {"name": "Faded Olive",  "hex": "#959A6B"},
            {"name": "Clay",         "hex": "#B7674A"},
        ],
        "avoid_colors": [
            {"name": "Electric Blue", "hex": "#007FFF"},
            {"name": "Bright White",  "hex": "#FDFDFD"},
            {"name": "True Black",    "hex": "#0A0A0A"},
            {"name": "Fuchsia",       "hex": "#C154C1"},
            {"name": "Ice Pink",      "hex": "#FFD1DC"},
        ],
        "cosmetics": [
            {"category": "Lipstick",   "brand": "MAC",               "shade": "Cherish",          "hex": "#B05A5A"},
            {"category": "Foundation", "brand": "Bobbi Brown",       "shade": "Warm Natural 3.5", "hex": "#C8A880"},
            {"category": "Eyeshadow",  "brand": "Charlotte Tilbury", "shade": "Smokey Eye 2",     "hex": "#8B6B61"},
            {"category": "Blush",      "brand": "Tarte",             "shade": "Blushing Bride",   "hex": "#D4906E"},
            {"category": "Eyeliner",   "brand": "L'Oreal",           "shade": "Brown Noir",       "hex": "#5C3317"},
        ],
    }
    return result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_sca_service():
    """Provide a mock SCAWorkflowService that always returns a successful result."""
    service = MagicMock()
    service.analyze = AsyncMock(return_value=_mock_season_result())
    return service


@pytest.fixture
def client(mock_sca_service):
    """
    TestClient with the SCA service dependency overridden so the real
    ML models are never loaded during tests.
    """
    # Override FastAPI's Depends(get_sca_service) to return our mock
    app.dependency_overrides[get_sca_service] = lambda: mock_sca_service

    # Use raise_server_exceptions=False so 500s are returned as responses
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    # Clean up overrides after each test
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tests – happy path
# ---------------------------------------------------------------------------

class TestAnalyzeEndpointSuccess:

    def test_analyze_jpeg_returns_200(self, client, mock_sca_service):
        response = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 200, response.text
        mock_sca_service.analyze.assert_awaited_once()

    def test_analyze_png_returns_200(self, client):
        response = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("photo.png", _make_png_bytes(), "image/png")},
        )
        assert response.status_code == 200, response.text

    def test_response_schema_shape(self, client):
        response = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        body = response.json()
        assert body["success"] is True
        assert "result" in body
        assert "metrics" in body
        assert "debug_info" in body

    def test_response_result_fields(self, client):
        body = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        ).json()
        result = body["result"]
        assert result["season"] == "soft_autumn"
        assert result["display_name"] == "Soft Autumn"
        assert result["confidence"] == pytest.approx(0.82)

    def test_response_metrics_dominant_colors(self, client):
        body = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        ).json()
        colors = body["metrics"]["dominant_colors"]
        assert len(colors["skin"]) == 3
        assert len(colors["hair"]) == 3
        assert len(colors["eye"]) == 3

    def test_response_debug_processing_time(self, client):
        body = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        ).json()
        assert body["debug_info"]["processing_time_ms"] == 850

    def test_response_includes_recommendations(self, client):
        """Response must contain color_palette and cosmetics inside recommendations."""
        body = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        ).json()
        assert "recommendations" in body, "Missing 'recommendations' key in response"
        recs = body["recommendations"]
        assert "color_palette" in recs, "Missing 'color_palette' inside recommendations"
        palette = recs["color_palette"]
        assert "best"    in palette, "Missing 'best' colour list"
        assert "neutral" in palette, "Missing 'neutral' colour list"
        assert "avoid"   in palette, "Missing 'avoid' colour list"
        assert len(palette["best"])    == 5
        assert len(palette["neutral"]) == 5
        assert len(palette["avoid"])   == 5
        assert "cosmetics" in recs, "Missing 'cosmetics' inside recommendations"
        assert len(recs["cosmetics"]) == 5

    def test_quiz_influence_in_response(self, client):
        """Response must contain quiz_influence as a float between 0 and 1."""
        body = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        ).json()
        assert "quiz_influence" in body, "Missing 'quiz_influence' in response"
        val = body["quiz_influence"]
        assert isinstance(val, float), f"quiz_influence should be float, got {type(val)}"
        assert 0.0 <= val <= 1.0, f"quiz_influence {val} out of [0, 1]"


# ---------------------------------------------------------------------------
# Tests – error paths
# ---------------------------------------------------------------------------

class TestAnalyzeEndpointErrors:

    def test_unsupported_file_type_returns_400(self, client):
        response = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("doc.pdf", b"%PDF-1.4 content", "application/pdf")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    def test_validation_error_from_service_returns_400(self, client, mock_sca_service):
        from app.services.sca_workflow_service import ValidationError
        mock_sca_service.analyze = AsyncMock(
            side_effect=ValidationError("Image too dark (mean luminance=25.0 < 40)")
        )
        response = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("dark.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 400
        assert "Image too dark" in response.json()["detail"]

    def test_unexpected_service_error_returns_500(self, client, mock_sca_service):
        mock_sca_service.analyze = AsyncMock(side_effect=RuntimeError("GPU OOM"))
        response = client.post(
            "/api/v1/sca/analyze",
            files={"file": ("selfie.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )
        assert response.status_code == 500

    def test_missing_file_returns_422(self, client):
        """No file at all → FastAPI validation error."""
        response = client.post("/api/v1/sca/analyze")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests – health check
# ---------------------------------------------------------------------------

class TestHealthCheck:

    def test_health_returns_200(self, client):
        response = client.get("/api/v1/sca/health")
        assert response.status_code == 200

    def test_health_response_shape(self, client):
        body = client.get("/api/v1/sca/health").json()
        assert body["status"] == "ok"
        assert body["service"] == "sca"
        assert "timestamp" in body
