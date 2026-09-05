# Development Plan

## NeuroVista-DR — SIH 2026

---

# M0 — Project Foundation

### Goal

Prepare the repository, documentation and development workflow.

### Tasks

- Repository structure
- README
- Problem statement
- Solution overview
- Architecture
- Prototype scope
- Development workflow
- Environment setup

### Current Owners

**Devraj**

---

# M1 — Core AI Pipeline

### Goal

Build the first functional retinal AI pipeline.

### Issues

```text
#3 Dataset
      ↓
#4 DR Classification
```

### Owner

**Devraj**

### Output

```text
Fundus Image
     ↓
Preprocessing
     ↓
DR Model
     ↓
ICDR 0–4
```

---

# M2 — Explainability + Application

### Goal

Turn the AI model into an understandable application.

### Issues

```text
#5 Grad-CAM
#6 Frontend
#7 Backend
```

### Ownership

```text
#5 → Devraj
#6 → Developer 2
#7 → Devraj
```

Frontend development can proceed using mock API responses while the AI pipeline is being developed.

---

# M3 — SIH Integration & Demo

### Goal

Create the complete internal-hackathon demonstration.

### Issues

```text
#8 Complete Integration
#9 End-to-End Testing
```

### Ownership

```text
#8 → Both
#9 → Both
```

---

# Development Dependency

```text
M0
 │
 ▼
#3 Dataset
 │
 ▼
#4 DR Model
 │
 ├──────────────► #5 Grad-CAM
 │
 └──────────────► #7 Backend
                         │
                         │
#6 Frontend ─────────────┘
                         │
                         ▼
                       #8
                  Integration
                         │
                         ▼
                       #9
                      Testing
```

---

# Parallel Development Strategy

The two developers should not block each other.

## Developer 1 — AI / Backend

```text
Dataset
   ↓
DR Model
   ↓
Grad-CAM
   ↓
Backend
```

## Developer 2 — Frontend

```text
Frontend
   ↓
Mock API
   ↓
UI States
   ↓
Result Visualization
```

Once both tracks are ready:

```text
AI + Backend
     +
Frontend
     ↓
Integration
```

---

# After Internal Shortlisting

If the team progresses beyond the internal hackathon, development expands to the remaining team members and the advanced SIH requirements.

Priority should then be given to:

1. Image quality assessment
2. Lesion-level analysis
3. Explainability improvement
4. Calibration
5. External validation
6. Ophthalmologist review
7. Simulink workflow simulation
8. Rural deployment constraints

The advanced scope should not delay the initial prototype.