# System Architecture

## NeuroVista-DR

---

## 1. Current Prototype Architecture

```text
                         USER
                          │
                          ▼
                    WEB FRONTEND
                          │
                    Upload Image
                          │
                          ▼
                     BACKEND API
                          │
                          ▼
                IMAGE QUALITY CHECK
                          │
                 ┌────────┴────────┐
                 │                 │
                PASS              FAIL
                 │                 │
                 ▼                 ▼
            PREPROCESSING     RECAPTURE MESSAGE
                 │
                 ▼
             DR MODEL
                 │
                 ▼
             ICDR 0–4
                 │
          ┌──────┴──────┐
          ▼             ▼
   REFERRAL RULE     GRAD-CAM
          │             │
          └──────┬──────┘
                 ▼
              API
                 │
                 ▼
              FRONTEND
                 │
                 ▼
             AI RESULT
```

---

## 2. Component Responsibilities

### Frontend

Responsible for:

- Image upload
- Image preview
- Processing state
- Result display
- Grad-CAM visualization
- Error handling
- Recapture guidance

---

### Backend

Responsible for:

- API endpoints
- Image validation
- Pipeline orchestration
- Communication between frontend and AI modules
- Response formatting
- Error handling

---

### MATLAB / AI Layer

Responsible for:

- Image processing
- Quality assessment
- Preprocessing
- DR classification
- Grad-CAM
- AI evaluation

---

## 3. AI Data Flow

```text
Raw Fundus Image
       ↓
Quality Assessment
       ↓
Preprocessing
       ↓
Model Input
       ↓
EfficientNet-B0
       ↓
Class Probabilities
       ↓
Predicted ICDR Grade
       ↓
Grad-CAM
```

---

## 4. Future Architecture

```text
Fundus Acquisition
        ↓
Image Quality Assessment
        ↓
Adaptive Enhancement
        ↓
Retinal Structure Analysis
        ↓
Lesion Detection / Segmentation
        ↓
DR Severity Grading
        ↓
Grad-CAM + Lesion Evidence
        ↓
Confidence Calibration
        ↓
Referable DR Decision
        ↓
Annotated Report
        ↓
Ophthalmologist Review
        ↓
Audit / Review Data
        ↓
Simulink Workflow Model
```

---

## 5. MATLAB Role

MATLAB is central to the retinal analysis pipeline because the SIH problem specifically requests a MATLAB-based solution.

Potential toolbox roles include:

| Toolbox | Role |
|---|---|
| Image Processing Toolbox | Enhancement and preprocessing |
| Computer Vision Toolbox | Image analysis and vision operations |
| Deep Learning Toolbox | DR model development and inference |
| Medical Imaging Toolbox | Medical image workflows |
| Statistics and Machine Learning Toolbox | Evaluation and calibration |
| Simulink | Workflow simulation |

---

## 6. Backend Integration

The backend should expose a stable interface between the frontend and AI pipeline.

Example:

```http
POST /analyze
```

Request:

```text
Fundus image
```

Response:

```json
{
  "success": true,
  "prediction": {
    "grade": 2,
    "severity": "Moderate NPDR",
    "referable": true,
    "confidence": 0.87
  },
  "explanation": {
    "gradcam_available": true
  }
}
```

---

## 7. Design Principle

The architecture should remain modular.

Each major component should be independently testable:

```text
Quality Module
      ↓
Classification Module
      ↓
Explainability Module
      ↓
Backend
      ↓
Frontend
```

This allows individual components to be improved without rewriting the complete application.