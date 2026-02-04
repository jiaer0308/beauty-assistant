#!/usr/bin/env python3
"""
BiSeNet Face Parser - Macro-Segmentation

Performs semantic segmentation using BiSeNet ONNX model to extract:
- Hair mask (class 17)
- Skin mask (classes 1 + 10: face + neck)
- Cloth mask (class 16)

This is Phase 1 of the Hybrid Vision pipeline.
"""

import cv2
import numpy as np
import onnxruntime as ort
from typing import Dict
import logging


logger = logging.getLogger(__name__)


class BiSeNetParser:
    """
    BiSeNet-based face parser for macro-segmentation
    
    Uses BiSeNet (ResNet34 backbone) ONNX model for semantic segmentation
    into 19 classes. Extracts hair, skin, and cloth regions.
    
    Model Details:
    - Input: RGB image (512x512)
    - Output: 19-class segmentation (512x512)
    - Classes used:
      * 1: Face skin
      * 10: Neck skin
      * 16: Cloth
      * 17: Hair
    
    Best Practices:
    - Use bilinear interpolation for resizing
    - Normalize to [0, 1] range
    - Transpose to NCHW format for ONNX
    - Apply morphological operations to clean masks
    """
    
    # BiSeNet class indices (from CelebAMask-HQ dataset)
    CLASS_FACE = 1
    CLASS_NOSE = 10
    CLASS_NECK = 14
    CLASS_CLOTH = 16
    CLASS_HAIR = 17
    
    # ImageNet Normalization Constants
    MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def __init__(self, session: ort.InferenceSession):
        """
        Initialize BiSeNet parser
        
        Args:
            session: ONNX InferenceSession for BiSeNet model
        """
        self.session = session
        self.input_size = (512, 512)  # BiSeNet required input size
        
        # Get input/output names from model
        self.input_name = session.get_inputs()[0].name
        self.output_name = session.get_outputs()[0].name
        
        logger.info(
            f"BiSeNet parser initialized "
            f"(input: {self.input_name}, output: {self.output_name})"
        )
    
    def parse(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Parse face into semantic regions
        
        Pipeline:
        1. Resize to 512x512 (bilinear interpolation)
        2. Normalize to [0, 1]
        3. Transpose to NCHW format
        4. Run ONNX inference
        5. Extract class masks
        6. Clean masks with morphology
        
        Args:
            image: RGB image (H, W, 3), any size
        
        Returns:
            Dictionary with binary masks:
            {
                "hair_mask": np.ndarray (H, W) - uint8 binary mask
                "skin_mask": np.ndarray (H, W) - face + neck combined
                "cloth_mask": np.ndarray (H, W)
            }
        
        Example:
            >>> parser = BiSeNetParser(onnx_session)
            >>> masks = parser.parse(image)
            >>> skin_pixels = image[masks["skin_mask"] == 1]
        """
        original_size = (image.shape[1], image.shape[0])  # (W, H)
        
        # Step 1: Preprocess image for BiSeNet
        input_tensor = self._preprocess(image)
        
        # Step 2: Run ONNX inference
        logger.debug("Running BiSeNet inference...")
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: input_tensor}
        )
        
        # Step 3: Postprocess segmentation
        segmentation = outputs[0][0]  # Shape: (19, 512, 512)
        
        # Get class predictions (argmax over channel dimension)
        class_predictions = segmentation.argmax(axis=0)  # Shape: (512, 512)
        
        # Step 4: Extract masks for each region
        masks = self._extract_masks(class_predictions, original_size)
        
        logger.info(
            f"BiSeNet parsing complete: "
            f"hair={masks['hair_mask'].sum()} pixels, "
            f"skin={masks['skin_mask'].sum()} pixels, "
            f"cloth={masks['cloth_mask'].sum()} pixels"
        )
        
        return masks
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for BiSeNet inference
        
        Best Practices:
        - Use INTER_LINEAR (bilinear) for smooth resizing
        - Normalize to [0, 1] range (not -1 to 1)
        - Use CHW format (channels first) for ONNX
        - Add batch dimension (NCHW)
        
        Args:
            image: RGB image (H, W, 3)
        
        Returns:
            Preprocessed tensor (1, 3, 512, 512) as float32
        """
        # Resize to 512x512 using bilinear interpolation
        # INTER_LINEAR is best for face images (smooth, no artifacts)
        resized = cv2.resize(
            image,
            self.input_size,
            interpolation=cv2.INTER_LINEAR
        )
        
        # Normalize to [0, 1]
        # BiSeNet expects pixel values in this range
        normalized = resized.astype(np.float32) / 255.0
        
        # Standardize (Subtract Mean, Divide Std)
        # ImageNet mean/std are channel-wise
        standardized = (normalized - self.MEAN) / self.STD

        # Transpose to CHW format (channels first)
        # OpenCV uses HWC, but ONNX models expect CHW
        chw = standardized.transpose(2, 0, 1)  # (3, 512, 512)
        
        # Add batch dimension
        nchw = chw[np.newaxis, ...]  # (1, 3, 512, 512)
        
        return nchw
    
    def _extract_masks(
        self,
        segmentation: np.ndarray,
        original_size: tuple
    ) -> Dict[str, np.ndarray]:
        """
        Extract binary masks from segmentation predictions
        
        Args:
            segmentation: Class predictions (512, 512) with values 0-18
            original_size: (width, height) of original image
        
        Returns:
            Dictionary of binary masks resized to original size
        """
        # Extract masks for each class
        hair_mask = (segmentation == self.CLASS_HAIR).astype(np.uint8)
        
        # Combine face and neck for complete skin mask
        # This ensures we capture full skin tone (not just face)
        skin_mask = np.isin(
            segmentation,
            [self.CLASS_FACE, self.CLASS_NOSE, self.CLASS_NECK]
        ).astype(np.uint8)
        
        cloth_mask = (segmentation == self.CLASS_CLOTH).astype(np.uint8)
        
        # Clean masks with morphological operations
        # Removes noise and small disconnected regions
        kernel = np.ones((3, 3), np.uint8)
        
        hair_mask = cv2.morphologyEx(
            hair_mask,
            cv2.MORPH_CLOSE,  # Fill small holes
            kernel,
            iterations=1
        )
        
        skin_mask = cv2.morphologyEx(
            skin_mask,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1
        )
        
        cloth_mask = cv2.morphologyEx(
            cloth_mask,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1
        )
        
        # Resize masks back to original image size
        # Use INTER_NEAREST to preserve binary nature
        hair_mask = cv2.resize(
            hair_mask,
            original_size,
            interpolation=cv2.INTER_NEAREST
        )
        
        skin_mask = cv2.resize(
            skin_mask,
            original_size,
            interpolation=cv2.INTER_NEAREST
        )
        
        cloth_mask = cv2.resize(
            cloth_mask,
            original_size,
            interpolation=cv2.INTER_NEAREST
        )
        
        return {
            "hair_mask": hair_mask,
            "skin_mask": skin_mask,
            "cloth_mask": cloth_mask
        }
