# Problem Statement

## SIH 2026 — PS 26038

### Explainable AI for Diabetic Retinopathy Screening in Rural India

---

## 1. Background

Diabetic retinopathy (DR) is a diabetes-related retinal complication that can cause vision impairment and blindness.

The SIH problem statement identifies a significant screening challenge in India due to the large diabetic population and limited availability of ophthalmologists, particularly in rural regions.

This creates a need for scalable screening systems that can assist healthcare workers in identifying patients who require specialist attention.

---

## 2. Problem

Current AI-based retinal screening systems can provide automated predictions, but several challenges remain:

- Variable fundus image quality
- Limited transparency of AI predictions
- Difficulty validating model decisions clinically
- Differences between imaging devices and populations
- Limited specialist availability in rural regions
- Need for efficient screening workflows

A useful system therefore needs to do more than simply classify an image.

---

## 3. SIH Technical Requirements

The problem statement specifies five major components.

### 3.1 Image Quality Assessment & Enhancement

The system should:

- Assess focus
- Assess illumination
- Assess field of view
- Apply adaptive enhancement
- Use techniques such as CLAHE, illumination normalization and denoising
- Reject ungradable images
- Provide recapture feedback

### 3.2 Retinal Structure and Lesion Analysis

The full solution should support:

- Optic disc localization
- Fovea localization
- Vessel segmentation
- Microaneurysm detection
- Exudate segmentation
- Hemorrhage classification
- Neovascularization detection

### 3.3 DR Severity Grading

The system should use the International Clinical DR severity scale:

```text
0 — No DR
1 — Mild NPDR
2 — Moderate NPDR
3 — Severe NPDR
4 — Proliferative DR
```

Referable DR is defined for this project as:

```text
Grade ≥ 2
```

The SIH problem statement specifies target performance of:

```text
Sensitivity > 90%
Specificity > 85%
```

for referable DR.

These values are **targets and not current project results**.

### 3.4 Explainability

The complete solution should provide:

- Grad-CAM attention maps
- Lesion-level evidence
- Clinical evidence associated with predictions
- Calibrated confidence
- Annotated reports
- Rapid ophthalmologist validation

### 3.5 Workflow Simulation

The complete SIH solution should eventually use Simulink to model:

- Image acquisition rate
- Bandwidth constraints
- Processing throughput
- Review capacity
- Screening workflow
- District-level resource requirements

---

## 4. Project Interpretation

NeuroVista-DR treats the problem as a **screening workflow problem**, rather than only a classification problem.

The system should answer:

```text
Is the image usable?
        ↓
What DR severity is predicted?
        ↓
Is specialist referral recommended?
        ↓
Why did the model make this prediction?
        ↓
Can a clinician quickly review the evidence?
```

---

## 5. Target Users

### Frontline Health Worker / Technician

Responsible for:

- Capturing or uploading fundus images
- Receiving image-quality feedback
- Sending usable images for screening

### Ophthalmologist / Retina Specialist

Responsible for:

- Reviewing AI results
- Checking model evidence
- Accepting or overriding the AI-assisted screening result

### District Health Program

Future system component:

- Monitoring screening throughput
- Understanding review capacity
- Planning resource allocation

---

## 6. Prototype Scope

The internal prototype intentionally implements a smaller subset of the full SIH requirements.

### Prototype

```text
Fundus Image
     ↓
Quality Gate
     ↓
Preprocessing
     ↓
DR Classification
     ↓
ICDR 0–4
     ↓
Referable Decision
     ↓
Grad-CAM
     ↓
Web Result
```

### Full Future System

```text
Fundus Image
     ↓
Quality Assessment
     ↓
Adaptive Enhancement
     ↓
Retinal Structures
     ↓
Lesion Analysis
     ↓
DR Grading
     ↓
Explainability
     ↓
Confidence Calibration
     ↓
Annotated Report
     ↓
Ophthalmologist Review
     ↓
Simulink Workflow Model
```

---

## 7. Important Limitations

The current prototype should not claim:

- Clinical diagnostic capability
- Clinical validation
- Regulatory approval
- Real-world deployment
- Universal generalization
- Achievement of SIH performance targets unless measured

All performance claims must be backed by actual evaluation results.