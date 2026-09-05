# NeuroVista-DR

### Explainable AI for Diabetic Retinopathy Screening in Rural India

**Team NeuroVista**  
**SIH 2026 — Problem Statement 26038**

> **Seeing Beyond. Thinking Ahead.**

---

## 📌 Overview

**NeuroVista-DR** is an AI-assisted diabetic retinopathy (DR) screening system designed for resource-constrained and rural healthcare environments.

The system analyzes retinal fundus images and aims to provide:

- Retinal image quality assessment
- Diabetic retinopathy severity grading
- Referable DR identification
- Visual explanation using Grad-CAM
- Clear screening results for frontline users
- A pathway for ophthalmologist review

The long-term system will expand toward lesion-level evidence, calibrated confidence, clinical validation, and workflow simulation using Simulink.

---

## 🎯 Problem Statement

Diabetic retinopathy is a major complication of diabetes that can lead to vision loss if not detected and managed appropriately.

Rural screening programs face challenges including:

- Limited availability of ophthalmologists
- Variable fundus image quality
- Limited access to specialist review
- Large screening volumes
- Lack of transparency in many AI-based systems

SIH Problem Statement 26038 asks for a **MATLAB-based retinal image analysis pipeline** addressing image quality, retinal structures, DR severity grading, explainability, and screening workflow simulation.

---

## 💡 Our Approach

NeuroVista-DR is designed around a **quality-gated, explainable screening pipeline**.

```text
Fundus Image
      ↓
Image Quality Assessment
      ↓
Preprocessing / Enhancement
      ↓
DR Classification
      ↓
ICDR Severity Grade (0–4)
      ↓
Referable DR Decision
      ↓
Grad-CAM Explanation
      ↓
Screening Result
      ↓
Future: Ophthalmologist Review
```

The system is intended as **AI-assisted screening/decision support**, not as a replacement for an ophthalmologist.

---

## 🧠 Current Prototype

The first internal-hackathon prototype focuses on a working end-to-end vertical slice:

### Included

- Fundus image upload
- Image quality gate
- Image preprocessing
- DR severity classification
- ICDR 0–4 grading
- Referable DR decision
- Grad-CAM visualization
- Web-based screening interface
- Backend API integration

### Planned After Shortlisting

- Lesion segmentation
- Lesion-level evidence
- Optic disc/fovea localization
- Calibrated confidence
- Annotated reports
- Ophthalmologist review workflow
- External dataset validation
- Rural/offline optimizations
- Simulink workflow simulation

---

## 🏗️ Architecture

```text
                    NEUROVISTA-DR
                         │
                         ▼
                  FUNDUS IMAGE
                         │
                         ▼
                IMAGE QUALITY GATE
                         │
                ┌────────┴────────┐
                │                 │
              GOOD              POOR
                │                 │
                │          Recapture Feedback
                │
                ▼
             PREPROCESSING
                │
                ▼
          DR CLASSIFICATION
                │
                ▼
             ICDR 0–4
                │
          ┌─────┴─────┐
          ▼           ▼
     REFERABLE?     GRAD-CAM
          │           │
          └─────┬─────┘
                ▼
          SCREENING RESULT
```

See [`docs/architecture.md`](docs/architecture.md) for details.

---

## 🧪 AI Methodology

The prototype uses transfer learning for retinal image classification.

### Initial classifier

**EfficientNet-B0**

The model will classify images into five International Clinical DR severity levels:

| Grade | Severity |
|---|---|
| 0 | No DR |
| 1 | Mild NPDR |
| 2 | Moderate NPDR |
| 3 | Severe NPDR |
| 4 | Proliferative DR |

For screening purposes:

```text
Referable DR = Grade ≥ 2
```

Model performance will be reported using measured evaluation results rather than assumed or target values.

---

## 🔍 Explainability

The prototype uses **Grad-CAM** to visualize image regions contributing to the model's prediction.

Grad-CAM should be interpreted as a model-attention visualization, not as definitive proof that a highlighted region represents a specific retinal lesion.

Future versions will strengthen explainability by combining model attention with lesion-level evidence.

---

## 📊 Evaluation

The project will evaluate:

- Accuracy
- Precision
- Recall / Sensitivity
- Specificity
- F1-score
- Confusion matrix
- ROC-AUC
- Calibration where applicable

The SIH problem statement specifies a target of:

- **>90% sensitivity**
- **>85% specificity**

for referable DR.

These are **project targets, not achieved results**.

---

## 🗂️ Repository Structure

```text
NeuroVista-DR/
│
├── assets/
│   ├── demo/
│   ├── diagrams/
│   └── screenshots/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│
├── models/
│   ├── grading/
│   ├── quality/
│   └── segmentation/
│
├── notebooks/
│
├── simulink/
│   ├── configs/
│   ├── models/
│   └── results/
│
├── src/
│   ├── backend/
│   ├── frontend/
│   └── matlab/
│
├── tests/
│
├── .gitignore
├── environment.yml
├── requirements.txt
└── README.md
```

---

## 🛠️ Technology Stack

### AI / Image Processing

- MATLAB
- MATLAB Image Processing Toolbox
- MATLAB Deep Learning Toolbox
- Computer Vision Toolbox
- Statistics and Machine Learning Toolbox

### Backend

- Python
- FastAPI
- MATLAB Engine integration where required

### Frontend

- React
- Vite

### Simulation

- MATLAB Simulink
- SimEvents where required

### Development

- Git
- GitHub
- VS Code

---

## 📚 Data

The project will use publicly available retinal datasets for research and development, subject to their respective licenses and usage conditions.

A major Indian-domain dataset under consideration is the **Indian Diabetic Retinopathy Image Dataset (IDRiD)**, which provides DR grading and lesion-related annotations.

Dataset selection, splitting, and licensing details are documented separately.

See:

```text
docs/
└── problem-statement.md
```

---

## ⚠️ Medical Disclaimer

NeuroVista-DR is a research and hackathon prototype.

It is intended to demonstrate an **AI-assisted screening and decision-support workflow**.

It is **not a clinically validated diagnostic system** and must not be used as a substitute for professional medical evaluation.

---

## 🚧 Project Status

**Current Phase: M0 — Project Foundation**

Development will proceed through:

```text
M0 — Project Foundation
        ↓
M1 — Core AI Pipeline
        ↓
M2 — Explainability + Application
        ↓
M3 — SIH Integration & Demo
```

---

## 👥 Team

### Team NeuroVista

**Seeing Beyond. Thinking Ahead.**

The project is being developed for SIH 2026 Problem Statement 26038.