#!/usr/bin/env python3
"""
MediaPipe Landmark Refiner - Micro-Refinement

Uses MediaPipe FaceMesh to perform "hole punch" technique:
- Detects precise eye and lip boundaries
- Removes them from BiSeNet skin mask
- Prevents color contamination from eyes/lips

This is Phase 2 of the Hybrid Vision pipeline.
"""

import cv2
import numpy as np
from typing import Dict, Optional, List
import logging


logger = logging.getLogger(__name__)


class LandmarkRefiner:
    """
    MediaPipe-based landmark refiner for micro-refinement
    
    Implements the "Hole Punch" technique:
    1. BiSeNet provides coarse skin mask
    2. MediaPipe detects precise facial landmarks
    3. Remove eye and lip regions from skin mask
    4. Result: Clean skin mask without color contamination
    
    Why "Hole Punch"?
    - BiSeNet can't differentiate eye/lip pixels from skin
    - Eye makeup and lip color would skew skin color analysis
    - MediaPipe's 478 landmarks provide precise boundaries
    
    Best Practices:
    - Use static_image_mode=True for single images
    - Enable refine_landmarks=True for iris detection
    - Process RGB images (MediaPipe expects RGB)
    - Use cv2.fillPoly for smooth polygon masks
    """
    
    # MediaPipe FaceMesh landmark indices
    # Based on MediaPipe canonical face model (478 landmarks)
    
    # Left eye contour (36 landmarks)
    LEFT_EYE_INDICES = [
        362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398
    ]    
    # Right eye contour (36 landmarks)
    RIGHT_EYE_INDICES = [
        33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246
    ]
    
    # Outer lip contour (20 landmarks)
    OUTER_LIP_INDICES = [
        61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 
        375, 321, 405, 314, 17, 84, 181, 91, 146
    ]
    
    # Inner lip contour (20 landmarks)
    INNER_LIP_INDICES = [
        78, 95, 88, 178, 87, 14, 317, 402, 318, 324,
        308, 415, 310, 311, 312, 13, 82, 81, 80, 191
    ]
    
    def __init__(self, face_mesh):
        """
        Initialize landmark refiner
        
        Args:
            face_mesh: MediaPipe FaceMesh instance
        """
        self.face_mesh = face_mesh
        logger.info("MediaPipe landmark refiner initialized")
    
    def refine_masks(
        self,
        image: np.ndarray,
        raw_skin_mask: np.ndarray
    ) -> Dict[str, Optional[np.ndarray]]:
        """
        Refine skin mask using MediaPipe landmarks
        
        The "Hole Punch" Process:
        1. Detect facial landmarks with MediaPipe
        2. Extract eye and lip polygons
        3. Create binary masks for eyes and lips
        4. Subtract them from raw skin mask
        5. Result: Clean skin without eye/lip contamination
        
        Args:
            image: RGB image (H, W, 3)
            raw_skin_mask: Coarse skin mask from BiSeNet (H, W)
        
        Returns:
            Dictionary:
            {
                "skin_mask": Refined skin mask (eyes/lips removed)
                "eye_mask": Combined eye region mask
                "lip_mask": Lip region mask
            }
            
            Note: If no face detected, returns original skin_mask
                  with None for eye_mask and lip_mask
        
        Example:
            >>> refiner = LandmarkRefiner(face_mesh)
            >>> masks = refiner.refine_masks(image, bisenet_skin_mask)
            >>> clean_skin = masks["skin_mask"]  # Ready for color extraction
        """
        height, width = image.shape[:2]
        
        # Step 1: Detect facial landmarks
        # MediaPipe expects RGB images
        results = self.face_mesh.process(image)
        
        if not results.multi_face_landmarks:
            logger.warning("No face landmarks detected, using raw skin mask")
            return {
                "skin_mask": raw_skin_mask,
                "eye_mask": None,
                "lip_mask": None
            }
        
        # Get landmarks from first detected face
        landmarks = results.multi_face_landmarks[0]
        
        # Step 2: Convert normalized landmarks to pixel coordinates
        points = self._landmarks_to_pixels(landmarks, width, height)
        
        # Step 3: Create eye and lip masks
        eye_mask = self._create_eye_mask(points, height, width)
        lip_mask = self._create_lip_mask(points, height, width)
        
        # Step 4: "Punch holes" - remove eyes and lips from skin
        # Using bitwise operations for efficiency
        refined_skin = raw_skin_mask.copy()
        refined_skin = cv2.bitwise_and(
            refined_skin,
            cv2.bitwise_not(eye_mask)
        )
        refined_skin = cv2.bitwise_and(
            refined_skin,
            cv2.bitwise_not(lip_mask)
        )
        
        # Log statistics
        original_pixels = raw_skin_mask.sum()
        refined_pixels = refined_skin.sum()
        removed_pixels = original_pixels - refined_pixels
        
        logger.info(
            f"Hole punch complete: removed {removed_pixels} pixels "
            f"({removed_pixels/original_pixels*100:.1f}% of skin mask)"
        )
        
        return {
            "skin_mask": refined_skin,
            "eye_mask": eye_mask,
            "lip_mask": lip_mask
        }
    
    def _landmarks_to_pixels(
        self,
        landmarks,
        width: int,
        height: int
    ) -> List[tuple]:
        """
        Convert MediaPipe normalized landmarks to pixel coordinates
        
        MediaPipe returns landmarks in normalized coordinates [0, 1].
        We need to convert them to pixel coordinates for mask creation.
        
        Args:
            landmarks: MediaPipe landmark list
            width: Image width
            height: Image height
        
        Returns:
            List of (x, y) pixel coordinates
        """
        points = []
        for landmark in landmarks.landmark:
            # Convert normalized [0, 1] to pixel coordinates
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            # Clamp to image boundaries (safety check)
            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))
            
            points.append((x, y))
        
        return points
    
    def _create_eye_mask(
        self,
        points: List[tuple],
        height: int,
        width: int
    ) -> np.ndarray:
        """
        Create combined eye region mask
        
        Best Practices:
        - Use fillPoly for smooth, antialiased edges
        - Combine left and right eyes into single mask
        - Add small margin around contour for safety
        
        Args:
            points: List of (x, y) pixel coordinates
            height: Mask height
            width: Mask width
        
        Returns:
            Binary mask (H, W) with eyes=1, rest=0
        """
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Extract left eye points
        left_eye = [points[i] for i in self.LEFT_EYE_INDICES if i < len(points)]
        
        # Extract right eye points
        right_eye = [points[i] for i in self.RIGHT_EYE_INDICES if i < len(points)]
        
        # Fill polygons
        if len(left_eye) > 0:
            cv2.fillPoly(mask, [np.array(left_eye, dtype=np.int32)], 1)
        
        if len(right_eye) > 0:
            cv2.fillPoly(mask, [np.array(right_eye, dtype=np.int32)], 1)
        
        # Optional: Dilate mask slightly to ensure complete coverage
        # This adds a small safety margin
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        
        return mask
    
    def _create_lip_mask(
        self,
        points: List[tuple],
        height: int,
        width: int
    ) -> np.ndarray:
        """
        Create lip region mask
        
        Uses outer lip contour for complete coverage.
        Inner lip contour is used for validation only.
        
        Args:
            points: List of (x, y) pixel coordinates
            height: Mask height
            width: Mask width
        
        Returns:
            Binary mask (H, W) with lips=1, rest=0
        """
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Extract outer lip points (provides complete coverage)
        outer_lip = [points[i] for i in self.OUTER_LIP_INDICES if i < len(points)]
        
        # Fill polygon
        if len(outer_lip) > 0:
            cv2.fillPoly(mask, [np.array(outer_lip, dtype=np.int32)], 1)
        
        # Optional: Dilate slightly for safety margin
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        
        return mask
    
    def get_landmark_count(self) -> int:
        """
        Get total number of landmarks detected by MediaPipe
        
        Returns:
            478 (with refine_landmarks=True)
            468 (without iris landmarks)
        """
        return 478  # With iris refinement enabled
