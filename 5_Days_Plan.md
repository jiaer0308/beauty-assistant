Here is a comprehensive 5-Day Implementation Guide for building a production-grade Seasonal Color Analysis (SCA) backend.

This plan integrates the **Hybrid Pipeline** strategy: using **BiSeNet** for volumetric segmentation (Hair/Cloth) and **MediaPipe** for geometric precision (Eyes/Lips/Skin refinement).

### **Part 1: The Architecture Mind Map**

This map visualizes the flow of data through the "Digital Esthetician" architecture.

```mermaid
mindmap
  root((SCA Backend<br/>Python 3.11))
    Infrastructure
      Docker (Debian-Slim)<br/>(No Alpine)
      FastAPI (Async)
      ONNX Runtime >= 1.17
    Phase 1: Hybrid Vision
      Step A: Macro-Segmentation
        BiSeNet (ONNX)
        Output: Hair Mask, Cloth Mask, Base Skin Mask
      Step B: Micro-Refinement
        MediaPipe Face Mesh
        Action: Subtract Lip/Eye Polygons from Skin Mask
        Action: Define Iris Region
    Phase 2: Color Engine
      Pre-processing
        Morphological Erosion (Shrink Masks)
      Extraction
        K-Means Clustering (k=3)
        Select Mid-tone Centroid
      Math
        sRGB -> Linear -> XYZ -> CIELAB
    Phase 3: Decision Logic
      Variables
        Hue (Skin b*)
        Value (Contrast Delta L*)
        Chroma (Eye/Hair C*)
      Classifier
        Rule-Based Decision Tree
```

---

### **Part 2: The 5-Day Implementation Plan**

#### **Day 1: Infrastructure & Environment Setup**
**Goal:** Initialize a containerized Python 3.11 environment that supports both ONNX and OpenCV without crashing.

1.  **Project Structure (Clean Architecture)**
    *   Set up the directory tree to separate the hybrid vision logic from the API:
        ```text
        src/
        ├── app/
        │   ├── api/v1/endpoints/   # FastAPI Routes
        │   ├── domain/services/    # Logic: Classifier, ColorTheory
        │   ├── infra/vision/       # BiSeNet & MediaPipe Wrappers
        │   └── main.py
        ```

2.  **Model Acquisition**
    *   Download the **BiSeNet (ResNet18 backbone)** `.onnx` model (often available via `uniface` or face-parsing repos).
    *   Configure `mediapipe` lazy loading.

#### **Day 2: The Macro-Segmentation (BiSeNet)**
**Goal:** Implement the "Heavy Lifter" to find Hair and Cloth, which MediaPipe cannot see.

1.  **BiSeNet Wrapper (`infra/vision/segmentation.py`)**
    *   **Preprocessing:** Resize input images to $512 \times 512$ and normalize (mean/std) as required by the specific trained model.
    *   **Inference:** Run the image through ONNX Runtime.

2.  **Mask Extraction Logic**
    *   Parse the output tensor (typically 19 classes):
        *   **Hair Mask:** Extract Class 17. *Why?* This captures volume and shape, essential for contrast calculation.
        *   **Cloth Mask:** Extract Class 16.
        *   **Base Skin Mask:** Combine Class 1 (Skin) + Class 10 (Nose). *Note:* Explicitly exclude Class 12/13 (Lips) to prevent "Lipstick Effect" contamination.

3.  **Upscaling**
    *   Resize the $512 \times 512$ masks back to original image dimensions using `cv2.INTER_NEAREST` to keep sharp edges.

#### **Day 3: Micro-Refinement (MediaPipe Fusion)**
**Goal:** Use MediaPipe to "clean" the BiSeNet masks and find the Iris.

1.  **Face Mesh Service**
    *   Initialize `FaceMesh` with `refine_landmarks=True`. *Critical:* This enables the Attention Mesh for the 10 distinct Iris landmarks.

2.  **The "Hole Punch" Technique (Hybrid Logic)**
    *   **Problem:** BiSeNet borders are sometimes soft.
    *   **Solution:** Generate a precise polygon using MediaPipe Lip Landmarks (indices 0-10 etc.).
    *   **Action:** Perform a bitwise `SUBTRACT` on the BiSeNet Skin Mask using the MediaPipe Lip Polygon. This ensures 0% lipstick contamination.

3.  **Iris Extraction**
    *   Use MediaPipe landmarks 468-478 to generate the Iris mask. BiSeNet is too coarse for this; MediaPipe is superior here.

4.  **Erosion**
    *   Apply `cv2.erode` (kernel $3 \times 3$) to all final masks. This shrinks the selection area, ensuring you only sample the "safe" center of the skin/hair, avoiding background bleeding.

#### **Day 4: Color Engineering (CIELAB)**
**Goal:** Convert raw pixels into usable physics data.

1.  **K-Means Clustering (Not Averaging)**
    *   **Action:** Run `sklearn.cluster.KMeans` ($k=3$) on the pixels from the Skin, Hair, and Eye masks.
    *   **Logic:** Discard the cluster with the highest $L^*$ (sweat/glare) and lowest $L^*$ (shadows). Keep the **Mid-tone** centroid.

2.  **Color Space Pipeline**
    *   **Transformation:** Implement the pipeline: $sRGB \rightarrow Linear RGB \rightarrow XYZ \rightarrow CIELAB$.
    *   *Why?* sRGB is not perceptually uniform. CIELAB separates Luminance ($L^*$) from Color ($a^*, b^*$), which is required for the seasonal formulas.

3.  **Metric Calculation**
    *   **Undertone:** Skin $b^*$ (Yellow-Blue axis).
    *   **Contrast:** Euclidean distance ($\Delta E$) between Skin $L^*$ and Hair $L^*$.
    *   **Intensity:** Chroma ($C^* = \sqrt{a^{*2} + b^{*2}}$) of the Eyes.

#### **Day 5: Business Logic & API**
**Goal:** Assemble the "Brain" and expose the endpoint.

1.  **The Decision Tree (`domain/services/classifier.py`)**
    *   Implement the hierarchical logic:
        *   **Root:** Warm ($b^* > Threshold$) vs. Cool.
        *   **Branch:** High Contrast ($\Delta L > 60$) vs. Low Contrast.
        *   **Leaf:** Clear (High Eye Chroma) vs. Muted.
    *   *Example:* IF (Cool) AND (High Contrast) $\rightarrow$ **Winter**.

2.  **FastAPI Endpoint**
    *   Create `POST /analyze`.
    *   **Response Schema:** Return the Season, Confidence, Color Palette, and crucially, **Landmarks**. Returning landmarks allows the frontend (e.g., Flutter/React) to draw AR overlays without re-processing the image.

### **Part 3：Requriment**

1. Computer Vision (The "Hybrid" Pipeline)
This workflow uses a dual-model approach to balance geometric precision with volumetric understanding.
• MediaPipe (mediapipe):
    ◦ Usage: Used for the Face Landmarker to detect 478 geometric points. It provides the "Attention Mesh" for precise Iris extraction and creates polygon masks for the cheeks and lips to ensure skin sampling excludes makeup.
• BiSeNet (via onnxruntime):
    ◦ Usage: The Bilateral Segmentation Network is used for semantic segmentation. It is the "Heavy Lifter" required to identify non-rigid volumetric features that MediaPipe misses, specifically Hair (Class 17) and Clothing (Class 16).
• ONNX Runtime (onnxruntime):
    ◦ Usage: The inference engine used to run the BiSeNet model.
    ◦ Version Requirement: You must use onnxruntime >= 1.17.0 to ensure compatibility with Python 3.11 wheels.
• UniFace (uniface):
    ◦ Usage: A production-ready wrapper for ONNX models. It abstracts the boilerplate code for downloading weights, normalizing images (to 512×512), and parsing the BiSeNet tensor output.
• OpenCV Headless (opencv-python-headless):
    ◦ Usage: Used for image manipulation (loading, color conversion, morphological erosion, polygon filling).
    ◦ Crucial Detail: You must use the headless variant. The standard opencv-python library includes GUI dependencies (Qt, X11) that will cause server-side Docker containers to crash.
2. Color Theory & Logic (The "Brain")
• Scikit-Learn (scikit-learn):
    ◦ Usage: Specifically the KMeans clustering algorithm. This is used to extract dominant color clusters (e.g., "True Skin," "Shadow," "Highlight") rather than using simple averages, which are prone to lighting errors.
• Scikit-Image (scikit-image):
    ◦ Usage: Provides color.rgb2lab for converting sRGB values into the CIELAB color space. This conversion is mathematically complex and requires specific reference illuminant handling (D65) which this library manages.
• NumPy (numpy):
    ◦ Usage: Handles high-performance array operations, specifically for converting image buffers from the API into matrices that OpenCV and Scikit-Learn can process.
2. API & Web Framework
• FastAPI (fastapi):
    ◦ Usage: The modern web framework chosen for its native support of asynchronous processing (async/await). This is critical for handling I/O-bound operations like high-resolution image uploads without blocking the server.
• Uvicorn (uvicorn):
    ◦ Usage: The high-performance ASGI server required to run the FastAPI application in production.
• Python-Multipart (python-multipart):
    ◦ Usage: Required by FastAPI to parse UploadFile form data (the raw image bytes) sent by the frontend.