#!/usr/bin/env python3
"""
SCA Workflow Service - Complete Seasonal Color Analysis Pipeline

Orchestrates the 4-phase hybrid pipeline:
Phase 0: Validation (Lighting checks)
Phase 1: Hybrid Vision (Alignment → BiSeNet → MediaPipe refinement)
Phase 2: Color Engine (K-Means extraction → RGB→LAB conversion)
Phase 3: Decision Logic (12-season classification)

This implements the user's specified workflow:
Step 1: MediaPipe (Face detection + rotation calculation)
Step 2: Image Preprocessing (Affine transformation → aligned 512x512 face)
Step 3: BiSeNet (Segmentation on aligned face)
Step 4: Color Extraction & Analysis (on aligned image + masks)
"""

import time
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import logging  
from sqlalchemy.orm import Session

# Internal imports
from app.ml_engine.loader import ModelLoader
from app.ml_engine.seasonal.face_aligner import FaceAligner
from app.ml_engine.seasonal.face_parser import BiSeNetParser
from app.ml_engine.seasonal.color import (
    extract_dominant_color,
    rgb_to_lab,
    calculate_chroma,
    get_skin_temperature_label
)
from app.ml_engine.seasonal.classifier import SeasonalColorClassifier

from app.domain.entities.season_result import SeasonResult
from app.domain.entities.user import User
from app.domain.value_objects.color_lab import ColorLAB
from app.schemas.sca import QuizData
from app.services.quiz_engine import QuizEngine
from app.services.recommendation_mapper import get_recommendation_mapper
from app.services.history_service import HistoryService


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when image validation fails"""
    pass


def validate_lighting(image: np.ndarray) -> Tuple[bool, str]:
    """
    Backend lighting validation using OpenCV statistics
    
    Checks:
    1. Mean luminance (too dark or overexposed)
    2. Variance (low contrast/blurry)
    
    Args:
        image: RGB image (H, W, 3)
    
    Returns:
        (is_valid, error_message)
    """
    # Convert to grayscale for analysis
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mean = gray.mean()
    variance = gray.var()
    
    logger.debug(f"Lighting stats: mean={mean:.1f}, variance={variance:.1f}")
    
    # Thresholds from workflow design
    if mean < 40:
        return False, f"Image too dark (mean luminance={mean:.1f} < 40)"
    
    if mean > 250:
        return False, f"Image overexposed (mean luminance={mean:.1f} > 250)"
    
    if variance < 10:
        return False, f"Low contrast or blurry (variance={variance:.1f} < 10)"
    
    return True, "Lighting acceptable"


class SCAWorkflowService:
    """
    Seasonal Color Analysis Workflow Service
    
    Implements the complete alignment-first pipeline:
    1. Face Alignment (MediaPipe → Affine Transform → 512x512)
    2. Segmentation (BiSeNet on aligned face)
    3. Color Extraction (K-Means on aligned image with masks)
    4. Classification (12-season decision tree)
    
    Key Design:
    - All processing happens on the ALIGNED FACE (512x512)
    - Masks are generated on aligned face and match perfectly
    - No need to map masks back to original (unless UI visualization)
    - Singleton pattern for model loading
    """
    
    def __init__(self):
        """
        Initialize workflow service with all required components
        
        Components:
        - ModelLoader: Singleton that loads BiSeNet ONNX + MediaPipe once
        - FaceAligner: MediaPipe-based alignment
        - BiSeNetParser: Segmentation on aligned face
        - SeasonClassifier: 12-season decision tree
        """
        logger.info("Initializing SCAWorkflowService...")
        
        # Load models (singleton - only loads once)
        self.models = ModelLoader()
        
        # Initialize pipeline components
        self.aligner = FaceAligner()
        self.parser = BiSeNetParser(self.models.bisenet_session)
        self.classifier = SeasonalColorClassifier()
        self.quiz_engine = QuizEngine()
        self.recommendation_mapper = get_recommendation_mapper()

        
        logger.info("SCAWorkflowService initialized successfully")
    
    async def analyze(
        self,
        image_bytes: bytes,
        db: Session,
        user_id: int,
        quiz_data: Optional[QuizData] = None,
    ) -> SeasonResult:
        """
        Execute complete SCA pipeline on uploaded image.

        Pipeline:
        Phase 0: Validation
        Phase 1: Hybrid Vision (Alignment + Segmentation + Refinement)
        Phase 2: Color Engine (Extraction + LAB conversion)
        Phase 3: Classification (Decision tree)
        Phase 4: Quiz Fusion + Recommendation Mapping  [NEW]

        Args:
            image_bytes: Raw image bytes (JPEG/PNG)
            db:          Database session
            user_id:     ID of the user performing analysis
            quiz_data:   Optional user quiz answers for score fusion

        Returns:
            SeasonResult entity with season, confidence, colors, metrics,
            recommendations, and quiz_influence

        Raises:
            ValidationError: If lighting is too poor or no face detected
        """
        start_time = time.time()
        logger.info("Starting SCA analysis pipeline for user %d...", user_id)
        
        # ========== Load Image ==========
        image = self._bytes_to_array(image_bytes)
        logger.info(f"Image loaded: shape={image.shape}, dtype={image.dtype}")
        
        # ========== Phase 0: Validation ==========
        logger.info("Phase 0: Validating lighting quality...")
        is_valid, msg = validate_lighting(image)
        if not is_valid:
            logger.error(f"Lighting validation failed: {msg}")
            raise ValidationError(msg)
        logger.info(f"✓ Lighting check passed: {msg}")
        
        # ========== Phase 1: Hybrid Vision ==========
        logger.info("Phase 1: Hybrid Vision Pipeline")
        
        # Step 1: Face Alignment (MediaPipe → Affine Transform)
        logger.info("  Step 1: MediaPipe face alignment...")
        alignment_result = self.aligner.detect_and_align(image)
        
        if not alignment_result["success"]:
            raise ValidationError("No face detected in image")
        
        aligned_face = alignment_result["aligned_image"]
        rotation_angle = alignment_result["rotation_angle"]
        landmarks = alignment_result["landmarks"]
        
        logger.info(
            f"  ✓ Face aligned: rotation={rotation_angle:.1f}°, "
            f"output_size={aligned_face.shape[:2]}, "
            f"landmarks={len(landmarks)}"
        )
        
        # Step 2: BiSeNet Segmentation (on aligned face)
        logger.info("  Step 2: BiSeNet segmentation on aligned face...")
        masks = self.parser.parse(aligned_face)
        
        hair_mask = masks["hair_mask"]
        raw_skin_mask = masks["skin_mask"]
        cloth_mask = masks["cloth_mask"]
        
        logger.info(
            f"  ✓ Segmentation complete: "
            f"hair={hair_mask.sum()} pixels, "
            f"skin={raw_skin_mask.sum()} pixels"
        )
        
        # Step 3: MediaPipe Refinement ("Hole Punch")
        # TODO: Implement MediaPipe mask refinement to remove eyes/lips from skin
        # For now, using raw BiSeNet skin mask
        logger.info("  Step 3: Mask refinement (TODO: implement hole punch)")
        refined_skin_mask = raw_skin_mask  # PLACEHOLDER
        
        # ========== Phase 2: Color Engine ==========
        logger.info("Phase 2: Color extraction and LAB conversion")
        
        # Extract dominant colors (K-Means clustering on aligned face)
        logger.info("  Extracting skin color...")
        skin_rgb = extract_dominant_color(aligned_face, refined_skin_mask)
        
        logger.info("  Extracting hair color...")
        hair_rgb = extract_dominant_color(aligned_face, hair_mask)
        
        # Note: Eye color extraction requires iris mask from MediaPipe
        # Using placeholder for now
        logger.info("  Eye color extraction (TODO: implement iris detection)")
        eye_rgb = np.array([100, 80, 60], dtype=np.uint8)  # PLACEHOLDER
        
        logger.info(
            f"  ✓ Colors extracted: "
            f"skin=RGB{skin_rgb}, hair=RGB{hair_rgb}, eye=RGB{eye_rgb}"
        )
        
        # Convert to CIELAB color space
        logger.info("  Converting RGB → LAB...")
        skin_lab = rgb_to_lab(skin_rgb)
        hair_lab = rgb_to_lab(hair_rgb)
        eye_chroma = calculate_chroma(eye_rgb)
        
        logger.info(
            f"  ✓ LAB conversion: "
            f"skin_L={skin_lab[0]:.1f}, skin_b={skin_lab[2]:.1f}, "
            f"hair_L={hair_lab[0]:.1f}, eye_chroma={eye_chroma:.1f}"
        )
        
        # ========== Phase 3: Classification ==========
        logger.info("Phase 3: Seasonal classification")
        
        # Calculate metrics
        contrast_score = abs(skin_lab[0] - hair_lab[0])
        skin_temperature = get_skin_temperature_label(skin_lab[1], skin_lab[2])
        
        logger.info(
            f"  Metrics: contrast={contrast_score:.1f}, "
            f"temperature={skin_temperature}"
        )
        
        # Classify into 12 seasons (classifier returns SeasonResult)
        classification_result = self.classifier.classify(
            skin_rgb,
            hair_rgb,
            eye_rgb
        )
        
        season = classification_result.season
        confidence = classification_result.confidence

        logger.info(
            f"  ✓ Image classification: {season.value} "
            f"(confidence={confidence:.2f})"
        )

        # ========== Phase 4: Quiz Fusion + Recommendation Mapping ==========
        logger.info("Phase 4: Quiz fusion and recommendation mapping")

        # Build image score map from classifier's raw scores
        image_scores: Dict[str, float] = getattr(
            classification_result, "all_scores", {season.value: confidence}
        )

        # Weighted fusion (30% quiz / 70% image)
        if quiz_data is not None:
            fused_scores = self.quiz_engine.compute_quiz_adjustments(
                quiz_data, image_scores
            )
            # Re-pick the top season after fusion
            top_season_key = max(fused_scores, key=fused_scores.get)  # type: ignore[arg-type]
            if top_season_key != season.value:
                logger.info(
                    "  Quiz fusion changed result: %s → %s",
                    season.value, top_season_key,
                )
                from app.domain.value_objects.seasonal_season import SeasonalSeason
                season = SeasonalSeason(top_season_key)
                confidence = float(fused_scores[top_season_key])

            quiz_influence = self.quiz_engine.compute_quiz_influence(
                quiz_data, image_scores, fused_scores
            )
        else:
            quiz_influence = 0.0
            logger.info("  No quiz data provided — using image scores only")

        # Load colour + cosmetic recommendations
        try:
            quiz_dict = quiz_data.dict() if quiz_data else None
            recs = self.recommendation_mapper.get_recommendations(
                season.value, db, quiz_dict
            )
        except ValueError:
            logger.warning("No recommendations for %s — returning empty dict", season.value)
            recs = {}

        logger.info(
            "  ✓ Phase 4 complete: season=%s, quiz_influence=%.2f",
            season.value, quiz_influence,
        )

        logger.info(
            f"  ✓ Final result: {season.value} "
            f"(confidence={confidence:.2f})"
        )
        
        # ========== Build Result Entity ==========
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        result = SeasonResult(
            season=season,
            confidence=confidence,
            contrast_score=contrast_score,
            skin_temperature=skin_temperature,
            skin_color=skin_rgb.tolist(),
            hair_color=hair_rgb.tolist(),
            eye_color=eye_rgb.tolist(),
            processing_time_ms=processing_time_ms,
            lighting_quality="good",
            timestamp=datetime.now(),
            # Additional metadata
            rotation_angle=rotation_angle,
            face_bbox=alignment_result["bbox"],
            # Recommendations and quiz influence [NEW]
            recommendations=recs,
            quiz_influence=quiz_influence,
        )
        
        logger.info(
            f"✓ SCA analysis complete in {processing_time_ms}ms: "
            f"{result.season.value} ({result.confidence:.0%})"
        )

        # ========== Task 7: Save History & Update User ==========
        # Mapping for Season enum to Database ID (1-12)
        season_id_map = {
            "bright_spring": 1,
            "true_spring": 2,
            "light_spring": 3,
            "light_summer": 4,
            "true_summer": 5,
            "soft_summer": 6,
            "soft_autumn": 7,
            "true_autumn": 8,
            "dark_autumn": 9,
            "dark_winter": 10,
            "true_winter": 11,
            "bright_winter": 12,
        }

#         bright_spring
# true_spring
# light_spring
# light_summer
# true_summer
# soft_summer
# soft_autumn
# true_autumn
# dark_autumn
# dark_winter
# true_winter
# bright_winter
        season_id = season_id_map.get(result.season.value)

        # Extract cosmetic_ids from the analysis result (if they exist)
        cosmetic_ids = [
            c.get("id") for c in result.recommendations.get("cosmetics", []) 
            if c.get("id") is not None
        ]

        # Save the analysis session to history
        HistoryService.save_session(
            db, user_id, "sca_scan", season_id, cosmetic_ids, None
        )

        # Update the User's current season in the database
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db_user.current_season_id = season_id
            db.add(db_user)
            db.commit()
            logger.info("Updated user %d current_season_id to %d", user_id, season_id)
        
        return result
    
    def _bytes_to_array(self, image_bytes: bytes) -> np.ndarray:
        """
        Convert image bytes to numpy RGB array
        
        Args:
            image_bytes: Raw JPEG/PNG bytes
        
        Returns:
            RGB image as numpy array (H, W, 3), dtype=uint8
        """
        # Use PIL to decode image
        pil_image = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB (handles RGBA, grayscale, etc.)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(pil_image)
        
        return image_array
