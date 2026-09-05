# Solution Overview

## NeuroVista-DR

NeuroVista-DR is an AI-assisted diabetic retinopathy screening platform designed around a **quality-aware and explainable retinal image analysis pipeline**.

---

## 1. Core Idea

Instead of directly sending every retinal image to a classifier, NeuroVista-DR introduces a quality gate before AI inference.

```text
                 FUNDUS IMAGE
                      │
                      ▼
             IMAGE QUALITY GATE
                      │
          ┌───────────┴───────────┐
          │                       │
        USABLE                UNGRADABLE
          │                       │
          ▼                       ▼
    PREPROCESSING          RECAPTURE FEEDBACK
          │
          ▼
     DR CLASSIFIER
          │
          ▼
      ICDR GRADE
          │
          ▼
   REFERABLE DECISION
          │
          ▼
       GRAD-CAM
          │
          ▼
       AI RESULT
```

This reduces the chance of blindly producing a prediction from an unusable retinal image.

---

## 2. Core Prototype Innovation

The prototype focuses on:

> **Quality-gated and explainable DR screening rather than classification alone.**

The system attempts to make the AI workflow more trustworthy by:

1. Checking whether the input image is suitable.
2. Producing an ICDR severity grade.
3. Identifying whether the case is referable.
4. Showing regions contributing to the prediction.

---

## 3. AI Pipeline

### Stage 1 — Image Input

Input:

```text
JPG / JPEG / PNG fundus image
```

---

### Stage 2 — Quality Assessment

The system evaluates image usability based on factors such as:

- Focus
- Illumination
- Field of view
- Image artifacts

Images that cannot be reliably analyzed should be rejected or flagged.

---

### Stage 3 — Preprocessing

Potential preprocessing operations include:

- Retinal field cropping
- Resizing
- Normalization
- Denoising
- Contrast enhancement

CLAHE and illumination normalization may be evaluated where appropriate.

---

### Stage 4 — DR Classification

The initial classifier uses transfer learning.

```text
Input
  ↓
EfficientNet-B0
  ↓
5-Class Output
```

Output:

```text
Grade 0
Grade 1
Grade 2
Grade 3
Grade 4
```

---

### Stage 5 — Referral Decision

The prototype converts the predicted grade into a screening signal:

```text
Grade < 2
    ↓
Non-referable

Grade ≥ 2
    ↓
Referable
```

This is a screening workflow rule and does not represent a clinical diagnosis.

---

### Stage 6 — Explainability

Grad-CAM is generated for the predicted class.

```text
Fundus Image
      +
Model Prediction
      ↓
Grad-CAM
      ↓
Attention Heatmap
      ↓
Overlay
```

The future system will add lesion-level evidence to strengthen the explanation.

---

## 4. Human-in-the-Loop Design

The long-term system is intended to support an ophthalmologist rather than replace one.

```text
AI Screening
     ↓
AI Result + Evidence
     ↓
Ophthalmologist
     ↓
Accept / Override
```

This review layer is particularly important for borderline or uncertain cases.

---

## 5. Rural Design Considerations

Future versions should consider:

- Low bandwidth
- Simple user interface
- Portable fundus cameras
- Offline-capable workflows
- Multilingual support
- Asynchronous specialist review

These are deployment considerations and are not all part of the initial two-person prototype.

---

## 6. Long-Term Direction

After the initial prototype, NeuroVista-DR can be expanded into:

```text
Quality Assessment
       ↓
Retinal Structure Analysis
       ↓
Lesion Segmentation
       ↓
DR Grading
       ↓
Explainability
       ↓
Confidence Calibration
       ↓
Clinical Review
       ↓
Workflow Simulation
```

The long-term architecture is designed to align with the complete SIH problem statement.