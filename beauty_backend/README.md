# Beauty Assistant Backend

Seasonal Color Analysis API using BiSeNet + MediaPipe Hybrid Pipeline Architecture.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env with your settings
```

### 3. Add BiSeNet Model

Download the BiSeNet ONNX model and place it at:
```
app/ml_engine/data/bisenet_resnet34.onnx
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## 📐 Architecture

```
beauty_backend/
├── app/
│   ├── core/           # Infrastructure (config, logging)
│   ├── domain/         # Business entities & value objects
│   ├── services/       # Use cases / business logic
│   ├── ml_engine/      # ML inference adapters
│   ├── api/            # Presentation layer (FastAPI)
│   └── schemas/        # DTOs (Pydantic models)
├── tests/              # Unit & integration tests
├── requirements.txt    # Python dependencies
└── .env               # Environment configuration
```

## 🔬 Technology Stack

- **Framework**: FastAPI 0.115.12
- **ML Inference**: ONNX Runtime 1.16.0
- **Computer Vision**: OpenCV 4.8.1, MediaPipe 0.10.9
- **Clustering**: scikit-learn 1.3.2
- **Validation**: Pydantic 2.10.3

## 📊 API Endpoints

### POST `/api/v1/analyze`

Analyzes an image for seasonal color classification.

**Request**: Multipart form data with image file

**Response**:
```json
{
  "status": "success",
  "data": {
    "result": {
      "season": "dark_autumn",
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
    }
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📚 Documentation

- [SCA Workflow Design](../docs/plans/2026-02-03-sca-workflow-design.md)
- [Implementation Plan](../.gemini/antigravity/brain/.../implementation_plan.md)
- [Rebuild Guide](../REBUILD_PROJECT_GUIDE.md)
