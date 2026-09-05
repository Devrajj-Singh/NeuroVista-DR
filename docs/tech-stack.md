# NeuroVista-DR — Technology Stack

## 1. Core AI / Medical Image Processing

| Technology | Purpose |
|---|---|
| MATLAB | Core retinal image analysis pipeline |
| Image Processing Toolbox | Image quality assessment, CLAHE, normalization, denoising |
| Computer Vision Toolbox | Retinal structure and lesion analysis support |
| Deep Learning Toolbox | DR grading, segmentation, Grad-CAM |
| Statistics and Machine Learning Toolbox | Calibration and evaluation |
| Simulink | Screening workflow simulation |
| SimEvents | Acquisition, bandwidth, throughput and review-capacity simulation |

## 2. AI Models

| Component | Model |
|---|---|
| DR Severity Grading | EfficientNet-B0 |
| Lesion Segmentation | U-Net |
| Image Quality Classification | Lightweight CNN |
| Explainability | Grad-CAM |
| Confidence Calibration | Temperature Scaling |

## 3. Python

Python is used for:
- Dataset preparation
- Data validation
- Augmentation
- Experimentation notebooks
- Supporting scripts
- Backend orchestration

MATLAB integration will use the MATLAB Engine API for Python where required.

## 4. Web Application

### Frontend
- React
- Vite

### Backend
- Python
- FastAPI

The backend remains a thin integration layer between the web application and the MATLAB AI pipeline.

## 5. Data Storage

- SQLite for the prototype
- PostgreSQL for a larger deployment

Stores:
- Patient/session metadata
- Image references
- AI results
- Review decisions
- Audit information

## 6. Development Tools

- Git
- GitHub
- VS Code
- Jupyter Notebooks
- Docker (where useful)

## 7. Datasets

- APTOS 2019
- IDRiD
- DeepDRiD
- EyePACS
- Messidor-2 for external evaluation

Dataset roles and splits are documented separately in the project documentation.

## 8. Important Architecture Rule

MATLAB is not an optional wrapper.

The core retinal image analysis and AI pipeline must genuinely execute through MATLAB because PS 26038 explicitly requires a MATLAB-based solution.

Python and the web stack support the MATLAB pipeline rather than replacing it.