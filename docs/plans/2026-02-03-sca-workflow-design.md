# Seasonal Color Analysis (SCA) Workflow Design
**Date:** 2026-02-03
**Status:** Approved for Implementation

## 1. Overview
This document defines the "Hybrid Pipeline" architecture for the Beauty Assistant Backend. It combines deep learning segmentation (BiSeNet) with geometric landmarking (MediaPipe) to achieve high-precision color analysis, robust to makeup and lighting variations.

---

## 2. Architecture & Performance
**Pattern:** Singleton Model Loader
To ensure low latency (<3s) on standard hardware:
- **Global Instance:** `BiSeNet` (ONNX) and `FaceMesh` are loaded *once* at server startup.
- **Sequential Execution:** Requests are processed linearly per worker to avoid GIL thrashing.
- **Memory Safety:** Explicit garbage collection of large tensors after each phase.

---

## 3. The Workflow Pipeline

### Phase 0: Validation (Fail Fast)
**Goal:** Reject unusable inputs before expensive processing.

1.  **Frontend Validation (Client-Side)**
    *   **Tool:** `google_mlkit_face_detection` (Flutter/Mobile).
    *   **Check:** Is there exactly 1 face? Is the face area > 20% of the screen?
    *   **Action:** If No -> Show UI error ("Please move closer" or "One person only"). Prevent upload.

2.  **Backend Validation (Server-Side)**
    *   **Tool:** OpenCV (Statistics).
    *   **Check (Lighting):** Convert to grayscale. Calculate Mean and Variance.
        *   `Mean < 40` (Too Dark) -> Reject (400).
        *   `Mean > 250` (Overexposed) -> Reject (400).
        *   `Variance < 10` (Low Contrast/Blurry) -> Reject (400).
    *   **Action:** Return specific error message to user ("Lighting is too poor for accurate results").

### Phase 1: Hybrid Vision (The "See" Phase)
**Goal:** Isolate Skin, Hair, and Eyes with pixel-perfect precision.

1.  **Step A: Macro-Segmentation (BiSeNet)**
    *   **Input:** $512 \times 512$ Normalized Tensor.
    *   **Model:** BiSeNet (ResNet backbone) via ONNX Runtime.
    *   **Output:**
        *   `Hair Mask` (Class 17) -> Captures volume.
        *   `Cloth Mask` (Class 16) -> For cloth removal/neutralization.
        *   `Raw Skin Mask` (Class 1 + 10) -> Rough skin area (includes lips/eyes).

2.  **Step B: Micro-Refinement (MediaPipe)**
    *   **Input:** Original Resolution Image.
    *   **Model:** MediaPipe Face Mesh (`refine_landmarks=True`).
    *   **Action 1 (The "Hole Punch"):**
        *   Generate Polygons for **Left Eye**, **Right Eye**, **Lips**.
        *   **Operation:** `Skin_Mask = Raw_Skin_Mask AND NOT (Eye_Poly OR Lip_Poly)`.
        *   *Result:* Skin mask with zero makeup/eye contamination.
    *   **Action 2 (Iris Extraction):**
        *   Use Iris Landmarks (468-478) to create a precise `Eye_Iris_Mask`.

### Phase 2: Color Engine (The "Measure" Phase)
**Goal:** Convert pixels into Physics-based logic variables.

1.  **Pre-processing**
    *   **Erosion:** Apply `cv2.erode` (3x3 kernel) to Skin and Hair masks. *Why?* Removes "border pixels" preventing background color bleeding.
    *   **Auto-White Balance (AWB):** Apply "Gray World" assumption to normalize color temperature if `auto_correct=True`.

2.  **Extraction (Smart Sampling)**
    *   **Algorithm:** `K-Means Clustering` (k=3) on masked pixels.
    *   **Selection:**
        *   Discard `Cluster_High_L` (Highlights/Sweat).
        *   Discard `Cluster_Low_L` (Shadows/Hair strands).
        *   **Keep `Cluster_Mid`** as the "True Color".

3.  **Math (Color Space)**
    *   Transform: $sRGB \rightarrow Linear \rightarrow XYZ \rightarrow CIELAB$.
    *   **Key Values Extracted:**
        *   `Skin_L`, `Skin_a`, `Skin_b`
        *   `Hair_L`
        *   `Eye_C` (Chroma)

### Phase 3: Decision Logic (The "Think" Phase)
**Goal:** Classify into one of 12 Seasons.

**Variables:**
- **Hue (Temp):** Based on `Skin_b` (Yellow-Blue axis).
- **Value (Contrast):** $\Delta L = |Skin_L - Hair_L|$.
- **Chroma (Intensity):** `Eye_C` (Saturation of iris).

**The Decision Tree:**

1.  **Root Split (Temperature):**
    *   IF `Skin_b > Warm_Threshold` (e.g., 18.0) AND `Eye_b > 0` $\rightarrow$ **WARM** (Spring/Autumn).
    *   ELSE $\rightarrow$ **COOL** (Summer/Winter).

2.  **Branch Split (Contrast/Value):**
    *   **IF COOL:**
        *   IF `Contrast > High_Threshold` (e.g., 60.0) $\rightarrow$ **Winter**.
        *   ELSE $\rightarrow$ **Summer**.
    *   **IF WARM:**
        *   IF `Contrast > Medium_Threshold` (e.g., 45.0) $\rightarrow$ **Autumn** (Deep).
        *   ELSE $\rightarrow$ **Spring** (Light).

3.  **Leaf Refinement (The 12 Sub-Seasons):**
    *   Use `Eye_Chroma` and relative `Hair_L` to distinguish subtypes (e.g., "Clear Winter" vs "Deep Winter").

---

## 4. API Response Schema
```json
{
  "status": "success",
  "data": {
    "result": {
      "season": "deep_autumn",
      "display_name": "Deep Autumn",
      "confidence": 0.88
    },
    "metrics": {
      "contrast_score": 52.4,
      "skin_temperature": "warm",
      "dominant_colors": {
        "skin": [210, 180, 160],
        "hair": [40, 30, 25],
        "eye": [85, 60, 40]
      }
    },
    "debug_info": {
      "lighting_quality": "good",
      "processing_time_ms": 1200
    }
  }
}
```
