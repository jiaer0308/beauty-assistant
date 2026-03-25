#!/usr/bin/env python3
"""
Face Alignment Service - MediaPipe-based Affine Transformation

This implements Step 1 & 2 of the user's pipeline:
1. MediaPipe Detection: Get 468 landmarks, calculate rotation angle
2. Affine Transformation: Rotate + crop + resize to 512x512

The aligned face is then used for BiSeNet segmentation and color extraction.
"""

import cv2
import numpy as np
import mediapipe as mp
import logging
import math
from typing import Dict, Tuple, Optional, List
from app.ml_engine.loader import ModelLoader

logger = logging.getLogger(__name__)


class FaceAligner:
    """
    Face alignment using MediaPipe Face Mesh
    
    Pipeline:
    1. Detect 468 facial landmarks using MediaPipe
    2. Calculate face rotation angle from eye corners (landmarks 33, 263)
    3. Calculate face bounding box with padding for hair
    4. Apply affine transformation to align face vertically
    5. Crop and resize to 512x512 for BiSeNet input
    
    This ensures consistent face orientation for accurate segmentation.
    """
    
    # Eye corner landmarks (used for rotation detection)
    LEFT_EYE_OUTER = 33   # Left eye outer corner
    RIGHT_EYE_OUTER = 263  # Right eye outer corner
    
    def __init__(self):
        """
        Initialize FaceAligner using the shared ModelLoader singleton.
        """
        # Use the singleton instance from ModelLoader
        self.face_mesh = ModelLoader().face_mesh
        logger.info("FaceAligner initialized (using shared MediaPipe instance)")
    
    def detect_and_align(
        self,
        image: np.ndarray,
        target_size: tuple = (512, 512),
        padding_factor: float = 0.3
    ) -> Dict[str, any]:
        """
        Detect face, calculate alignment, and return aligned image
        
        Args:
            image: RGB image (H, W, 3)
            target_size: Output size for aligned face (default: 512x512)
            padding_factor: Extra space around face bounding box (0.3 = 30%)
                           Needed to capture hair region
        
        Returns:
            {
                "aligned_image": np.ndarray (512, 512, 3) - Rotated and cropped face
                "rotation_angle": float - Detected rotation angle in degrees
                "rotation_matrix": np.ndarray (2, 3) - Affine transform matrix
                "face_center": tuple (x, y) - Face center in original image
                "bbox": tuple (x, y, w, h) - Face bounding box in original
                "landmarks": list - 468 facial landmark coordinates
                "success": bool - Whether alignment succeeded
            }
        
        Example:
            >>> aligner = FaceAligner()
            >>> result = aligner.detect_and_align(image)
            >>> aligned_face = result["aligned_image"]
            >>> angle = result["rotation_angle"]
            >>> print(f"Face rotated by {angle:.1f}°")
        """
        h, w = image.shape[:2]
        
        # Step 1: Detect facial landmarks using MediaPipe
        logger.debug("Running MediaPipe Face Mesh detection...")
        results = self.face_mesh.process(image)
        
        if not results.multi_face_landmarks:
            logger.warning("No face detected by MediaPipe")
            return {
                "aligned_image": None,
                "rotation_angle": 0.0,
                "rotation_matrix": None,
                "face_center": (w//2, h//2),
                "bbox": (0, 0, w, h),
                "landmarks": [],
                "success": False
            }
        
        # Extract landmarks (already in pixel coordinates)
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = [
            (int(lm.x * w), int(lm.y * h))
            for lm in face_landmarks.landmark
        ]
        
        # Step 2: Calculate rotation angle from eye corners
        rotation_angle = self._calculate_rotation_angle(landmarks)
        logger.info(f"Detected face rotation: {rotation_angle:.2f}°")
        
        # Step 3: Calculate face bounding box with padding
        bbox = self._calculate_bounding_box(landmarks, w, h, padding_factor)
        x, y, box_w, box_h = bbox
        
        # Calculate face center
        face_center = (x + box_w // 2, y + box_h // 2)
        
        # Step 4: Create rotation matrix for affine transformation
        # Rotate around face center to align eyes horizontally
        rotation_matrix = cv2.getRotationMatrix2D(face_center, rotation_angle, scale=1.0)
        
        # Step 5: Apply affine transformation (rotation)
        logger.debug("Applying affine transformation...")
        rotated_image = cv2.warpAffine(
            image,
            rotation_matrix,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        # Step 6: Crop face region from rotated image
        # Apply same rotation to bbox center
        rotated_center = rotation_matrix @ np.array([[face_center[0]], [face_center[1]], [1]])
        new_center_x = int(rotated_center[0, 0])
        new_center_y = int(rotated_center[1, 0])
        
        # Calculate crop region (centered on rotated face)
        half_w = box_w // 2
        half_h = box_h // 2
        
        crop_x1 = max(0, new_center_x - half_w)
        crop_y1 = max(0, new_center_y - half_h)
        crop_x2 = min(w, new_center_x + half_w)
        crop_y2 = min(h, new_center_y + half_h)
        
        cropped_face = rotated_image[crop_y1:crop_y2, crop_x1:crop_x2]
        
        # Step 7: Resize to target size (512x512 for BiSeNet)
        logger.debug(f"Resizing from {cropped_face.shape[:2]} to {target_size}...")
        aligned_face = cv2.resize(
            cropped_face,
            target_size,
            interpolation=cv2.INTER_LINEAR
        )
        
        logger.info(
            f"Face alignment complete: "
            f"rotation={rotation_angle:.1f}°, "
            f"bbox={bbox}, "
            f"output_size={target_size}"
        )
        
        return {
            "aligned_image": aligned_face,
            "rotation_angle": rotation_angle,
            "rotation_matrix": rotation_matrix,
            "face_center": face_center,
            "bbox": bbox,
            "landmarks": landmarks,
            "success": True
        }
    
    def _calculate_rotation_angle(self, landmarks: list) -> float:
        """
        Calculate face rotation angle from eye corners
        
        Uses left and right eye outer corners (landmarks 33 and 263) to detect
        if the face is tilted. A perfectly vertical face has eyes horizontally aligned.
        
        Args:
            landmarks: List of (x, y) tuples for 468 landmarks
        
        Returns:
            Rotation angle in degrees (positive = clockwise tilt)
        
        Math:
            angle = arctan2(dy, dx)
            where dy = right_eye.y - left_eye.y
                  dx = right_eye.x - left_eye.x
        """
        left_eye = landmarks[self.LEFT_EYE_OUTER]
        right_eye = landmarks[self.RIGHT_EYE_OUTER]
        
        # Calculate slope between eye corners
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        
        # Calculate angle in radians, then convert to degrees
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        logger.debug(
            f"Eye corners: left={left_eye}, right={right_eye}, "
            f"slope=dy/dx={dy}/{dx}={dy/dx if dx != 0 else 'inf'}, "
            f"angle={angle_deg:.2f}°"
        )
        
        return angle_deg
    
    def _calculate_bounding_box(
        self,
        landmarks: list,
        img_width: int,
        img_height: int,
        padding_factor: float = 0.3
    ) -> Tuple[int, int, int, int]:
        """
        Calculate bounding box around face with padding
        
        The padding is crucial because BiSeNet needs to see the full hair region,
        which extends beyond the face landmarks.
        
        Args:
            landmarks: List of (x, y) landmark coordinates
            img_width: Original image width
            img_height: Original image height
            padding_factor: Expansion factor (0.3 = add 30% on each side)
        
        Returns:
            (x, y, width, height) bounding box
        """
        # Find min/max coordinates across all landmarks
        xs = [lm[0] for lm in landmarks]
        ys = [lm[1] for lm in landmarks]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        # Calculate current size
        box_w = x_max - x_min
        box_h = y_max - y_min
        
        # Apply padding
        padding_w = int(box_w * padding_factor)
        padding_h = int(box_h * padding_factor)
        
        # Expand box (with bounds checking)
        x = max(0, x_min - padding_w)
        y = max(0, y_min - padding_h)
        w = min(img_width - x, box_w + 2 * padding_w)
        h = min(img_height - y, box_h + 2 * padding_h)
        
        logger.debug(
            f"Bounding box: original=({x_min},{y_min},{box_w},{box_h}), "
            f"padded=({x},{y},{w},{h}), "
            f"padding={padding_factor*100:.0f}%"
        )
        
        return (x, y, w, h)
    
    def get_landmarks_for_regions(self, landmarks: list) -> Dict[str, list]:
        """
        Extract specific landmark groups for MediaPipe refinement
        
        Returns landmark indices for:
        - Left eye polygon
        - Right eye polygon
        - Lips polygon
        - Iris regions
        
        These will be used in Phase 1 Step B (MediaPipe "hole punch")
        
        Args:
            landmarks: List of 468 (x, y) tuples
        
        Returns:
            {
                "left_eye": [...],
                "right_eye": [...],
                "lips": [...],
                "left_iris": [...],
                "right_iris": [...]
            }
        """
        # MediaPipe Face Mesh landmark indices
        # Reference: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
        
        return {
            # Eye contours (for "hole punch")
            "left_eye": list(range(33, 133)),    # Left eye region
            "right_eye": list(range(362, 263, -1)),  # Right eye region
            
            # Lip contours
            "lips": list(range(61, 291)),  # Outer + inner lips
            
            # Iris landmarks (requires refine_landmarks=True)
            "left_iris": list(range(468, 473)),   # Left iris (5 points)
            "right_iris": list(range(473, 478))   # Right iris (5 points)
        }
