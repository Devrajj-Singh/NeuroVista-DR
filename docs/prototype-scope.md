# Prototype Scope

## NeuroVista-DR — Internal Hackathon Prototype

---

## 1. Purpose

The current objective is to build a convincing, functional prototype for the **internal SIH 2026 selection**.

Only two team members are currently developing the prototype.

Therefore, the first version intentionally focuses on a small number of connected features rather than attempting to implement the entire SIH problem statement.

---

# 2. MUST HAVE — Current Prototype

## A. Image Input

- Fundus image upload
- Supported image formats
- Image preview
- Basic input validation

---

## B. Image Quality Gate

The prototype should perform a genuine quality check.

At minimum, evaluate:

- Blur / focus
- Basic illumination
- Retinal field visibility

Output:

```text
GOOD
```

or

```text
UNGRADABLE
```

For an ungradable image:

```text
Reject image
+
Explain reason
+
Request recapture
```

---

## C. DR Classification

Five-class ICDR grading:

```text
0 — No DR
1 — Mild NPDR
2 — Moderate NPDR
3 — Severe NPDR
4 — Proliferative DR
```

---

## D. Referable DR

Prototype rule:

```text
Grade ≥ 2 → Referable
Grade < 2 → Non-referable
```

---

## E. Explainability

Implement:

```text
Grad-CAM
```

Display:

```text
Original Image
+
Grad-CAM Overlay
```

---

## F. Frontend

The user should be able to:

```text
Upload
  ↓
Analyze
  ↓
Wait
  ↓
View Quality
  ↓
View DR Grade
  ↓
View Referral Decision
  ↓
View Grad-CAM
```

---

## G. Backend

Provide an API connecting:

```text
Frontend ↔ AI Pipeline
```

---

# 3. SHOULD HAVE — Only If Time Allows

- Better image-quality scoring
- Improved preprocessing
- Confidence display
- Better result visualization
- Basic report generation
- Improved error handling
- Demo screenshots
- Basic model comparison

---

# 4. POST-SHORTLISTING

These features should NOT block the first prototype.

### Advanced Retinal Analysis

- Lesion segmentation
- Microaneurysm detection
- Hemorrhage analysis
- Exudate segmentation
- Vessel segmentation
- Optic disc localization
- Fovea localization
- Neovascularization detection

### Explainability

- Lesion-level evidence
- Clinical evidence mapping
- Confidence calibration
- Annotated reports
- Explanation validation

### Clinical Workflow

- Ophthalmologist dashboard
- Accept / override
- Review reason
- Audit trail

### Validation

- External dataset testing
- Cross-dataset testing
- Population/domain-shift analysis
- Bias analysis
- Calibration analysis

### Rural Deployment

- Offline inference
- Low-bandwidth optimization
- Multilingual interface
- Portable-camera integration
- Teleophthalmology workflow

### Simulation

- Simulink screening workflow
- Acquisition rate
- Bandwidth
- Processing throughput
- Ophthalmologist capacity
- District-level resource allocation

---

# 5. EXPLICITLY OUT OF CURRENT SCOPE

The following should not be implemented during the initial two-person prototype unless the core flow is already stable:

```text
SHAP
LRP
Multiple XAI methods
Federated learning
Differential privacy
Production cloud infrastructure
Regulatory certification
Clinical trials
Large-scale deployment
```

---

# 6. Definition of Prototype Complete

The prototype is considered complete when this works reliably:

```text
        FUNDUS IMAGE
              ↓
        QUALITY CHECK
              ↓
        PREPROCESSING
              ↓
        DR CLASSIFICATION
              ↓
          ICDR 0–4
              ↓
       REFERABLE DECISION
              ↓
           GRAD-CAM
              ↓
        WEB RESULT
```

A demo user should be able to complete the workflow without manually executing unrelated scripts.

---

# 7. Medical Safety Boundary

The prototype must always be described as:

> **AI-assisted diabetic retinopathy screening / decision support.**

It must not be presented as:

> An autonomous diagnostic system.

Actual model performance must be reported honestly using measured test results.