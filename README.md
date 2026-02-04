# beauty-assistant

## Seasonal Color Analysis (SCA) Workflow
1. Face Detection (FE) [google_mlkit_face_detection]
2. Face Parsing (BE) [MediaPipe Face Mesh]
3. Color Extraction (BE) [OpenCV + NumPy] 
  - Convert the extracted ROIs from RGB to CIELAB (Lab) color space.
4. Classification (BE) [ scikit-learn (Decision Tree)]
5. AR Color-Try-On (FE) [Flutter CustomPainter + MediaPipe Face Mesh ]