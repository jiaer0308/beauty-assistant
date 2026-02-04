Beauty Assistant Backend - Implementation Plan
Based on: SCA Hybrid Pipeline Architecture (2026-02-03)
Status: Ready for Implementation

📋 Executive Summary
Current State: ❌ Empty skeleton (all Python files are 0 bytes)
Target State: ✅ Production-ready SCA backend with <3s processing time

Architecture Pattern: Clean Architecture + Hexagonal (Ports & Adapters)
ML Pipeline: BiSeNet (segmentation) + MediaPipe FaceMesh (landmarks) → CIELAB → 12-Season Classification

🏗️ Implementation Phases
Phase 1: Infrastructure Foundation (Day 1, 4 hours)
1.1 Project Setup & Dependencies
# Create structure
beauty_backend/
├── app/
│   ├── core/           # Infrastructure
│   ├── domain/         # Business entities
│   ├── services/       # Use cases
│   ├── ml_engine/      # ML adapters
│   ├── api/            # Presentation
│   └── data/           # Static files
Key Files:

requirements.txt
 - Pin all dependencies
.env.example - Environment template
app/core/config.py
 - Pydantic Settings
app/core/logger.py - Structured logging
Dependencies (requirements.txt):

# API Framework
fastapi==0.115.12
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.7.0
# Computer Vision
opencv-python==4.8.1.78
numpy==1.24.3
mediapipe==0.10.9
# ML Inference
onnxruntime==1.16.0  # BiSeNet
scikit-learn==1.3.2  # K-Means
# Image Processing
Pillow==11.0.0
# Utilities
python-dotenv==1.0.1
Deliverables:

 Virtual environment activated
 All dependencies installed
 Configuration management working
 Logging system initialized
Phase 2: Domain Layer (Day 1, 3 hours)
Implement pure business logic with zero external dependencies.

2.1 Value Objects (app/domain/value_objects/)
color_lab.py - CIELAB color representation:

from dataclasses import dataclass
@dataclass(frozen=True)
class ColorLAB:
    """CIELAB color space value object"""
    L: float  # Lightness (0-100)
    a: float  # Green-Red axis
    b: float  # Blue-Yellow axis
    
    def __post_init__(self):
        if not (0 <= self.L <= 100):
            raise ValueError(f"L must be 0-100, got {self.L}")
seasonal_season.py - 12 seasons enum:

from enum import Enum
class SeasonalSeason(str, Enum):
    # Winter family
    DEEP_WINTER = "deep_winter"
    COOL_WINTER = "cool_winter"
    CLEAR_WINTER = "clear_winter"
    
    # Summer family
    LIGHT_SUMMER = "light_summer"
    COOL_SUMMER = "cool_summer"
    SOFT_SUMMER = "soft_summer"
    
    # Autumn family
    DEEP_AUTUMN = "deep_autumn"
    WARM_AUTUMN = "warm_autumn"
    SOFT_AUTUMN = "soft_autumn"
    
    # Spring family
    LIGHT_SPRING = "light_spring"
    WARM_SPRING = "warm_spring"
    CLEAR_SPRING = "clear_spring"
2.2 Entities (app/domain/entities/)
season_result.py - Analysis result entity:

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
@dataclass
class SeasonResult:
    """Seasonal color analysis result"""
    season: SeasonalSeason
    display_name: str
    confidence: float
    
    # Color metrics
    contrast_score: float
    skin_temperature: str  # "warm" or "cool"
    
    # Dominant colors (RGB)
    skin_color: List[int]
    hair_color: List[int]
    eye_color: List[int]
    
    # Processing metadata
    processing_time_ms: int
    lighting_quality: str  # "good", "acceptable", "poor"
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to API response format"""
        return {
            "result": {
                "season": self.season.value,
                "display_name": self.display_name,
                "confidence": round(self.confidence, 2)
            },
            "metrics": {
                "contrast_score": round(self.contrast_score, 1),
                "skin_temperature": self.skin_temperature,
                "dominant_colors": {
                    "skin": self.skin_color,
                    "hair": self.hair_color,
                    "eye": self.eye_color
                }
            },
            "debug_info": {
                "lighting_quality": self.lighting_quality,
                "processing_time_ms": self.processing_time_ms
            }
        }
Deliverables:

 All value objects implemented with validation
 SeasonalSeason enum with 12 seasons
 SeasonResult entity with to_dict() method
 Unit tests for domain logic
Phase 3: ML Engine Core (Day 2, 8 hours)
Implement the Hybrid Pipeline from the workflow design.

3.1 Singleton Model Loader (app/ml_engine/loader.py)
import onnxruntime as ort
import mediapipe as mp
from pathlib import Path
import logging
class ModelLoader:
    """Singleton: Load heavy models once at startup"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
    
    def _initialize_models(self):
        """Load BiSeNet and MediaPipe once"""
        logger = logging.getLogger(__name__)
        
        # BiSeNet ONNX model
        model_path = Path(__file__).parent / "data" / "bisenet_resnet34.onnx"
        self.bisenet_session = ort.InferenceSession(
            str(model_path),
            providers=['CPUExecutionProvider']
        )
        logger.info("✅ BiSeNet loaded")
        
        # MediaPipe FaceMesh
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        logger.info("✅ MediaPipe FaceMesh loaded")
3.2 Phase 0: Validation (app/ml_engine/validation.py)
Backend validation logic (called before expensive processing):

import cv2
import numpy as np
def validate_lighting(image: np.ndarray) -> tuple[bool, str]:
    """
    Check lighting quality using OpenCV statistics
    Returns: (is_valid, error_message)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mean = gray.mean()
    variance = gray.var()
    
    if mean < 40:
        return False, "Image too dark (mean={:.1f})".format(mean)
    if mean > 250:
        return False, "Image overexposed (mean={:.1f})".format(mean)
    if variance < 10:
        return False, "Low contrast/blurry (variance={:.1f})".format(variance)
    
    return True, "Lighting acceptable"
3.3 Phase 1: Hybrid Vision (app/ml_engine/seasonal/)
face_parser.py
 - BiSeNet segmentation:

class BiSeNetParser:
    """Macro-segmentation using BiSeNet ONNX"""
    
    def __init__(self, session: ort.InferenceSession):
        self.session = session
        self.input_size = (512, 512)
    
    def parse(self, image: np.ndarray) -> dict:
        """
        Returns:
            {
                "hair_mask": np.ndarray (binary mask),
                "skin_mask": np.ndarray (binary mask),
                "cloth_mask": np.ndarray (binary mask)
            }
        """
        # Preprocess: resize to 512x512, normalize
        resized = cv2.resize(image, self.input_size)
        normalized = resized / 255.0
        input_tensor = normalized.transpose(2, 0, 1)[np.newaxis, ...]
        
        # ONNX inference
        outputs = self.session.run(None, {"input": input_tensor.astype(np.float32)})
        segmentation = outputs[0][0].argmax(axis=0)
        
        # Extract masks (BiSeNet class indices)
        return {
            "hair_mask": (segmentation == 17).astype(np.uint8),
            "skin_mask": np.isin(segmentation, [1, 10]).astype(np.uint8),
            "cloth_mask": (segmentation == 16).astype(np.uint8)
        }
landmark_refiner.py - MediaPipe micro-refinement:

class LandmarkRefiner:
    """Micro-refinement using MediaPipe FaceMesh"""
    
    def __init__(self, face_mesh):
        self.face_mesh = face_mesh
    
    def refine_masks(self, image: np.ndarray, raw_skin_mask: np.ndarray) -> dict:
        """
        The "Hole Punch": Remove eyes/lips from skin mask
        Returns: {
            "skin_mask": np.ndarray (refined),
            "eye_mask": np.ndarray,
            "lip_mask": np.ndarray
        }
        """
        results = self.face_mesh.process(image)
        if not results.multi_face_landmarks:
            return {"skin_mask": raw_skin_mask, "eye_mask": None, "lip_mask": None}
        
        landmarks = results.multi_face_landmarks[0]
        h, w = image.shape[:2]
        
        # Get pixel coordinates
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]
        
        # Create eye polygon (landmarks 33-133 for left, 362-263 for right)
        left_eye = [points[i] for i in range(33, 133)]
        right_eye = [points[i] for i in range(362, 263, -1)]
        
        # Create lip polygon (landmarks 61-291)
        lip = [points[i] for i in range(61, 291)]
        
        # Draw masks
        eye_mask = np.zeros_like(raw_skin_mask)
        cv2.fillPoly(eye_mask, [np.array(left_eye + right_eye)], 1)
        
        lip_mask = np.zeros_like(raw_skin_mask)
        cv2.fillPoly(lip_mask, [np.array(lip)], 1)
        
        # "Punch holes" - remove eyes and lips from skin
        refined_skin = raw_skin_mask & ~(eye_mask | lip_mask)
        
        return {
            "skin_mask": refined_skin,
            "eye_mask": eye_mask,
            "lip_mask": lip_mask
        }
3.4 Phase 2: Color Engine (
app/ml_engine/seasonal/color.py
)
Color extraction with K-Means:

from sklearn.cluster import KMeans
def extract_dominant_color(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Smart sampling using K-Means clustering
    Args:
        image: RGB image
        mask: Binary mask (1 = region of interest)
    Returns:
        RGB color [R, G, B]
    """
    # Apply erosion to remove border pixels
    kernel = np.ones((3, 3), np.uint8)
    eroded_mask = cv2.erode(mask, kernel, iterations=1)
    
    # Extract pixels
    pixels = image[eroded_mask == 1]
    
    if len(pixels) < 10:
        return np.array([0, 0, 0])
    
    # K-Means with k=3
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get cluster centers and their sizes
    centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    counts = np.bincount(labels)
    
    # Convert to LAB to get lightness
    centers_lab = rgb_to_lab(centers)
    
    # Discard highest L (highlights) and lowest L (shadows)
    sorted_idx = np.argsort(centers_lab[:, 0])
    mid_cluster_idx = sorted_idx[1]  # Middle lightness
    
    return centers[mid_cluster_idx].astype(int)
RGB → CIELAB conversion:

def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """
    Convert RGB to CIELAB color space
    Pipeline: sRGB → Linear RGB → XYZ → LAB
    """
    # Step 1: sRGB to Linear RGB (gamma correction)
    linear = rgb / 255.0
    linear = np.where(
        linear <= 0.04045,
        linear / 12.92,
        ((linear + 0.055) / 1.055) ** 2.4
    )
    
    # Step 2: Linear RGB to XYZ (D65 illuminant)
    M = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041]
    ])
    xyz = linear @ M.T
    
    # Step 3: XYZ to LAB
    xyz_ref = np.array([0.95047, 1.00000, 1.08883])  # D65
    xyz_norm = xyz / xyz_ref
    
    f = np.where(
        xyz_norm > 0.008856,
        xyz_norm ** (1/3),
        (7.787 * xyz_norm) + (16/116)
    )
    
    L = 116 * f[1] - 16
    a = 500 * (f[0] - f[1])
    b = 200 * (f[1] - f[2])
    
    return np.array([L, a, b])
3.5 Phase 3: Decision Logic (
app/ml_engine/seasonal/classifier.py
)
12-Season Decision Tree:

class SeasonClassifier:
    """Classification logic based on contrast, temperature, chroma"""
    
    # Thresholds from workflow design
    WARM_THRESHOLD = 18.0  # Skin_b value
    HIGH_CONTRAST = 60.0   # ΔL threshold
    MEDIUM_CONTRAST = 45.0
    
    def classify(
        self,
        skin_lab: ColorLAB,
        hair_lab: ColorLAB,
        eye_chroma: float
    ) -> tuple[SeasonalSeason, float]:
        """
        Returns: (season, confidence)
        """
        # Calculate metrics
        contrast = abs(skin_lab.L - hair_lab.L)
        is_warm = (skin_lab.b > self.WARM_THRESHOLD)
        
        # Root split: Temperature
        if is_warm:
            season = self._classify_warm(contrast, eye_chroma)
        else:
            season = self._classify_cool(contrast, eye_chroma)
        
        confidence = self._calculate_confidence(skin_lab, hair_lab, eye_chroma)
        return season, confidence
    
    def _classify_cool(self, contrast: float, eye_chroma: float) -> SeasonalSeason:
        """Cool family: Winter or Summer"""
        if contrast > self.HIGH_CONTRAST:
            # Winter family
            if eye_chroma > 40:
                return SeasonalSeason.CLEAR_WINTER
            else:
                return SeasonalSeason.DEEP_WINTER
        else:
            # Summer family
            if eye_chroma < 20:
                return SeasonalSeason.SOFT_SUMMER
            else:
                return SeasonalSeason.LIGHT_SUMMER
    
    def _classify_warm(self, contrast: float, eye_chroma: float) -> SeasonalSeason:
        """Warm family: Spring or Autumn"""
        if contrast > self.MEDIUM_CONTRAST:
            # Autumn family
            return SeasonalSeason.DEEP_AUTUMN
        else:
            # Spring family
            if eye_chroma > 35:
                return SeasonalSeason.CLEAR_SPRING
            else:
                return SeasonalSeason.LIGHT_SPRING
Deliverables:

 ModelLoader singleton working
 Lighting validation implemented
 BiSeNet segmentation producing masks
 MediaPipe refinement "punching holes" correctly
 K-Means color extraction working
 RGB → CIELAB conversion validated
 12-season classifier passing test cases
Phase 4: Service Layer (Day 3, 4 hours)
Use Case: Orchestrate the entire workflow.

app/services/sca_workflow_service.py:

class SCAWorkflowService:
    """
    Orchestrates the complete SCA pipeline
    Clean Architecture: Use Case layer
    """
    
    def __init__(self):
        self.models = ModelLoader()
        self.parser = BiSeNetParser(self.models.bisenet_session)
        self.refiner = LandmarkRefiner(self.models.face_mesh)
        self.classifier = SeasonClassifier()
    
    async def analyze(self, image_bytes: bytes) -> SeasonResult:
        """
        Execute 4-phase pipeline
        Returns: SeasonResult entity
        """
        start_time = time.time()
        
        # Load image
        image = self._bytes_to_array(image_bytes)
        
        # Phase 0: Validation
        is_valid, msg = validate_lighting(image)
        if not is_valid:
            raise ValidationError(msg)
        
        # Phase 1: Hybrid Vision
        masks = self.parser.parse(image)
        refined = self.refiner.refine_masks(image, masks["skin_mask"])
        
        # Phase 2: Color Engine
        skin_rgb = extract_dominant_color(image, refined["skin_mask"])
        hair_rgb = extract_dominant_color(image, masks["hair_mask"])
        eye_rgb = extract_dominant_color(image, refined["eye_mask"])
        
        skin_lab = rgb_to_lab(skin_rgb)
        hair_lab = rgb_to_lab(hair_rgb)
        eye_chroma = calculate_chroma(eye_rgb)
        
        # Phase 3: Classification
        season, confidence = self.classifier.classify(
            ColorLAB(*skin_lab),
            ColorLAB(*hair_lab),
            eye_chroma
        )
        
        # Build result entity
        processing_time = int((time.time() - start_time) * 1000)
        return SeasonResult(
            season=season,
            display_name=season.value.replace("_", " ").title(),
            confidence=confidence,
            contrast_score=abs(skin_lab[0] - hair_lab[0]),
            skin_temperature="warm" if skin_lab[2] > 18 else "cool",
            skin_color=skin_rgb.tolist(),
            hair_color=hair_rgb.tolist(),
            eye_color=eye_rgb.tolist(),
            processing_time_ms=processing_time,
            lighting_quality="good",
            timestamp=datetime.now()
        )
Deliverables:

 SCAWorkflowService orchestrating all phases
 Error handling for each phase
 Processing time tracking
 Integration test with sample images
Phase 5: API Layer (Day 3, 3 hours)
Presentation layer - FastAPI endpoints.

app/api/v1/analysis.py
:

from fastapi import APIRouter, UploadFile, HTTPException
from app.services.sca_workflow_service import SCAWorkflowService
from app.schemas.analysis_dto import AnalysisResponse
router = APIRouter()
service = SCAWorkflowService()
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_seasonal_color(file: UploadFile):
    """
    Seasonal Color Analysis endpoint
    Implements the API schema from workflow design document
    """
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Invalid file type")
    
    # Read bytes
    image_bytes = await file.read()
    
    # Execute workflow
    try:
        result = await service.analyze(image_bytes)
        return {"status": "success", "data": result.to_dict()}
    except ValidationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")
app/schemas/analysis_dto.py:

from pydantic import BaseModel
from typing import List, Dict
class DominantColors(BaseModel):
    skin: List[int]
    hair: List[int]
    eye: List[int]
class Metrics(BaseModel):
    contrast_score: float
    skin_temperature: str
    dominant_colors: DominantColors
class Result(BaseModel):
    season: str
    display_name: str
    confidence: float
class DebugInfo(BaseModel):
    lighting_quality: str
    processing_time_ms: int
class AnalysisData(BaseModel):
    result: Result
    metrics: Metrics
    debug_info: DebugInfo
class AnalysisResponse(BaseModel):
    status: str
    data: AnalysisData
app/main.py - Application entry:

from fastapi import FastAPI
from app.api.v1 import analysis
from app.core.config import settings
from app.ml_engine.loader import ModelLoader
app = FastAPI(title=settings.app_name, version=settings.app_version)
@app.on_event("startup")
async def startup():
    """Load models once at startup"""
    ModelLoader()  # Singleton initialization
    
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
@app.get("/health")
def health_check():
    return {"status": "healthy"}
Deliverables:

 POST /api/v1/analyze endpoint working
 Response matches workflow design schema
 File upload validation
 Health check endpoint
 OpenAPI docs auto-generated
Phase 6: Testing & Validation (Day 4, 4 hours)
6.1 Unit Tests
Test color conversion:

def test_rgb_to_lab():
    """Validate CIELAB conversion against known values"""
    # Pure red in sRGB
    rgb = np.array([255, 0, 0])
    lab = rgb_to_lab(rgb)
    
    assert 53 < lab[0] < 54  # L≈53.24
    assert 80 < lab[1] < 81  # a≈80.09
    assert 67 < lab[2] < 68  # b≈67.20
Test classifier:

def test_classify_deep_winter():
    """Test deep winter classification"""
    classifier = SeasonClassifier()
    
    # Deep Winter characteristics: high contrast, cool, low chroma
    skin = ColorLAB(L=70, a=5, b=10)   # Light, cool skin
    hair = ColorLAB(L=15, a=0, b=0)    # Dark hair
    eye_chroma = 25
    
    season, confidence = classifier.classify(skin, hair, eye_chroma)
    assert season == SeasonalSeason.DEEP_WINTER
    assert confidence > 0.7
6.2 Integration Test
End-to-end workflow test:

@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete pipeline with real image"""
    service = SCAWorkflowService()
    
    # Load test image
    with open("tests/fixtures/deep_winter_sample.jpg", "rb") as f:
        image_bytes = f.read()
    
    # Execute
    result = await service.analyze(image_bytes)
    
    # Assertions
    assert result.season in SeasonalSeason
    assert 0 <= result.confidence <= 1
    assert result.processing_time_ms < 3000  # <3s requirement
    assert len(result.skin_color) == 3
Deliverables:

 All unit tests passing
 Integration tests with sample images
 Performance validated (<3s)
 Test coverage > 80%
✅ Acceptance Criteria
Functional
 API Endpoint: POST /api/v1/analyze returns JSON matching spec
 Hybrid Pipeline: BiSeNet + MediaPipe integration
 Color Math: RGB → CIELAB conversion validated
 Classification: 12-season decision tree implemented
 Performance: <3s processing time
 Validation: Lighting checks reject poor images
Architectural
 Clean Architecture: Strict layer separation (Presentation → Use Cases → Domain → Infrastructure)
 Dependency Inversion: ML engine accessed through interfaces
 Singleton Pattern: ModelLoader loads models once
 Testability: Core logic testable without FastAPI/ONNX
Quality
 Type Safety: All DTOs use Pydantic
 API Docs: Auto-generated OpenAPI spec
 Logging: Structured logging for debugging
 Error Handling: Specific error messages per phase
📊 Estimated Timeline
Phase	Tasks	Time	Dependencies
1. Infrastructure	Setup, deps, config	4h	None
2. Domain Layer	Entities, value objects	3h	Phase 1
3. ML Engine	BiSeNet, MediaPipe, color math	8h	Phase 1
4. Service Layer	SCAWorkflowService	4h	Phase 2, 3
5. API Layer	FastAPI routes, schemas	3h	Phase 4
6. Testing	Unit + integration tests	4h	All phases
Total: ~26 hours (~3.5 days solo development)

🚨 Critical Success Factors
BiSeNet ONNX Model: Must have bisenet_resnet34.onnx in app/ml_engine/data/
MediaPipe Version: Use mediapipe==0.10.9 (stable FaceMesh API)
Color Accuracy: Validate CIELAB conversion with test vectors
Memory Management: Explicit gc.collect() after each request (per workflow design)
Sequential Execution: One request per worker (avoid GIL thrashing)
📚 References
Workflow Design: 
docs/plans/2026-02-03-sca-workflow-design.md
Rebuild Guide: 
REBUILD_PROJECT_GUIDE.md
 (implementation details)
Architecture Patterns: Clean Architecture + Hexagonal Architecture