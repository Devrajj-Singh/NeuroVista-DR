# NeuroVista-DR — Dataset Strategy

## 1. Purpose

This document defines the dataset strategy for the NeuroVista-DR project under SIH 2026 Problem Statement 26038.

The objective is to establish a reproducible and leakage-aware dataset pipeline for:

- Diabetic Retinopathy (DR) severity grading
- Image quality assessment
- Lesion-level analysis
- Explainability validation
- External generalization evaluation

Datasets will not be blindly merged. Each dataset has a defined role based on its labels, annotations, imaging characteristics, and intended use.

---

## 2. Dataset Roles

| Dataset | Primary Role | Current Status |
|---|---|---|
| APTOS 2019 | Primary DR grading and rural-India context | Planned |
| IDRiD | Indian DR grading and lesion-level ground truth | Primary |
| DeepDRiD | Image-quality assessment and quality-aware screening | Planned |
| EyePACS | Large-scale pretraining / robustness | Future |
| Messidor-2 | External validation | Future / Held Out |

---

## 3. APTOS 2019

### Purpose

APTOS 2019 will be considered a primary source for DR severity classification because it is directly aligned with the rural-India screening context of the problem.

The dataset provides fundus photographs with clinician-assigned DR severity labels from 0 to 4:

| Grade | Description |
|---:|---|
| 0 | No DR |
| 1 | Mild DR |
| 2 | Moderate DR |
| 3 | Severe DR |
| 4 | Proliferative DR |

The official Kaggle competition describes variation in image quality, including artifacts, focus, exposure, and camera conditions.

### Planned Role

- DR grading
- Model development
- Internal validation
- Prototype demonstration

### Important Constraint

APTOS data will not automatically be merged with every other dataset.

Label compatibility, metadata, class distributions, image quality, and dataset-specific characteristics must be inspected before cross-dataset training.

### Source

APTOS 2019 Blindness Detection:

https://www.kaggle.com/competitions/aptos2019-blindness-detection/data

---

## 4. IDRiD

### Purpose

IDRiD is the primary dataset for Indian-domain validation and lesion-level explainability development.

The dataset contains 516 color fundus images captured at an eye clinic in Nanded, Maharashtra, India.

### Available Ground Truth

All 516 images have image-level grading.

The dataset provides:

- DR severity grading
- Diabetic macular edema grading
- Lesion annotations
- Optic disc information
- Fovea center information

The pixel-level lesion subset contains annotations for:

- Microaneurysms (MA)
- Hard exudates (EX)
- Hemorrhages (HE)
- Soft exudates (SE)

The available pixel-level lesion annotations cover 81 images.

### Planned Role

- Indian-domain validation
- Lesion segmentation experiments
- Explainability validation
- Grad-CAM / lesion evidence comparison
- DR grading validation
- Optic disc and fovea localization support

### Split Strategy

The official grading split will be respected where applicable.

Patient/image relationships and dataset metadata must be inspected before creating any additional splits.

### Source

Official IDRiD dataset page:

https://idrid.grand-challenge.org/Data/

### License

IDRiD is released under a Creative Commons Attribution 4.0 International License.

Appropriate attribution must be retained in project documentation.

---

## 5. DeepDRiD

### Purpose

DeepDRiD will primarily support the image-quality component of NeuroVista-DR.

The dataset contains:

- 2,000 regular fundus images from 500 patients
- 256 ultra-widefield images from 128 patients
- DR grading annotations
- Image-quality annotations

The quality assessment covers factors including:

- Artifacts
- Clarity
- Field definition
- Overall image quality

### Planned Role

- Image quality classifier development
- Quality-gating experiments
- Recapture/rejection logic
- Robustness testing
- Device and acquisition-condition analysis

### Important Constraint

DeepDRiD should not automatically become the primary DR grading dataset.

Its strongest role for this project is the quality-aware screening component.

### Source

DeepDRiD project repository:

https://github.com/deepdrdoc/DeepDRiD

Research publication:

https://doi.org/10.1016/j.patter.2022.100512

---

## 6. EyePACS

### Purpose

EyePACS may be used later as a large-scale source for model pretraining and robustness experiments.

### Planned Role

- Backbone pretraining
- Large-scale representation learning
- Robustness experiments
- Dataset-domain comparison

### Current Status

EyePACS is not required for the first prototype dataset pipeline.

It will only be introduced after the smaller, better-characterized datasets have been validated.

### Important Constraint

EyePACS labels may be noisier and its acquisition conditions differ from IDRiD and APTOS.

It must therefore not automatically be treated as equivalent ground truth across all datasets.

---

## 7. Messidor-2

### Purpose

Messidor-2 is reserved for external validation.

It must remain completely separate from model development.

### External Validation Rule

Messidor-2 must not be used for:

- Training
- Hyperparameter tuning
- Threshold selection
- Architecture selection
- Model development
- Iterative experimentation

Using the dataset for tuning would invalidate its role as an external test set.

### Current Status

**Held out for future external validation.**

No model-development decisions should be based on Messidor-2 results before the final evaluation stage.

---

## 8. Dataset Combination Strategy

The datasets will not initially be combined into one large training pool.

Instead, each dataset will retain a clearly defined role based on its annotation quality, domain characteristics, and purpose within the NeuroVista-DR pipeline.

### Initial Strategy

```text
APTOS 2019
     |
     +-- DR severity grading
     +-- Model development
     +-- Internal evaluation

IDRiD
     |
     +-- Indian-domain validation
     +-- Lesion ground truth
     +-- DR grading
     +-- Explainability validation

DeepDRiD
     |
     +-- Image-quality assessment
     +-- Quality-gating
     +-- Robustness analysis

EyePACS
     |
     +-- Future large-scale pretraining / robustness

Messidor-2
     |
     +-- External validation only
```

### Cross-Dataset Training

Cross-dataset training may be considered later, but only after verifying:

- Label compatibility
- Class definitions
- Class distributions
- Image quality
- Image acquisition characteristics
- Patient-level relationships
- Duplicate images
- Dataset-specific preprocessing requirements

Datasets must not be blindly concatenated.

---

## 9. Data Leakage Prevention

Medical imaging datasets require careful handling to prevent data leakage.

NeuroVista-DR will attempt to prevent:

- Patient-level leakage
- Duplicate-image leakage
- Near-duplicate leakage
- Augmented-image leakage
- Test-set leakage
- External-validation leakage

### Patient-Level Separation

Where patient identifiers are available, images belonging to the same patient should remain within the same dataset split.

For example:

```text
Patient A
 ├── Image 1
 ├── Image 2
 └── Image 3
```

should not be split as:

```text
Training   -> Image 1
Validation -> Image 2
Testing    -> Image 3
```

Instead, all images belonging to Patient A should remain within a single split.

### Duplicate Detection

The validation pipeline should check for:

- Exact duplicate files
- Duplicate image content
- Near-duplicate images
- Multiple versions of the same original image

Possible techniques include:

- File hashing
- Perceptual hashing
- Image similarity analysis
- Metadata comparison

Duplicate detection should be performed before creating new dataset splits where practical.

---

## 10. Dataset Split Strategy

Dataset splits will be created only after dataset integrity and label validation.

The project will maintain explicit split definitions under:

```text
data/
└── splits/
```

Example:

```text
data/
└── splits/
    ├── aptos_train.csv
    ├── aptos_validation.csv
    ├── aptos_test.csv
    └── external_validation.csv
```

The exact split proportions will be determined after inspecting:

- Dataset size
- Class distribution
- Patient structure
- Existing official dataset splits

Where an official dataset split is provided and appropriate, it should be preserved rather than unnecessarily recreated.

---

## 11. Test Set Policy

The final test set must remain isolated from model development.

The test set should not be repeatedly used for:

- Hyperparameter tuning
- Architecture selection
- Threshold selection
- Data augmentation selection
- Feature engineering
- Repeated model selection

The test set should only be used after the development process has been sufficiently finalized.

---

## 12. External Validation Policy

External validation is separate from internal testing.

The distinction is:

```text
Internal Test Set
        |
        +-- Measures performance within the development data environment

External Validation Set
        |
        +-- Measures generalization to a different dataset/environment
```

A model performing well on an internal test set does not necessarily demonstrate strong external generalization.

Messidor-2 will therefore remain isolated until the final external evaluation stage.

---

## 13. Domain Shift and Bias

The target deployment environment for NeuroVista-DR is rural India.

Therefore, the project must consider differences between datasets and the eventual deployment environment.

Potential sources of domain shift include:

- Camera manufacturer
- Camera model
- Field of view
- Image resolution
- Illumination
- Image compression
- Acquisition protocol
- Image quality
- Patient population
- Disease prevalence
- Clinical setting
- Dataset-specific annotation practices

Performance differences between datasets should be treated as useful information for understanding model limitations.

The project will not claim universal clinical generalization based only on performance from public datasets.

---

## 14. Image Preprocessing Strategy

Preprocessing will be applied consistently and reproducibly.

Potential preprocessing operations include:

- Image resizing
- Retinal-region cropping
- Illumination normalization
- Contrast enhancement
- CLAHE
- Denoising
- Pixel normalization

The intended preprocessing pipeline is:

```text
Raw Fundus Image
       |
       v
Image Integrity Check
       |
       v
Retinal Region Processing
       |
       v
Resize
       |
       v
Illumination / Contrast Processing
       |
       v
Normalization
       |
       v
Model Input
```

Original raw images must remain unchanged.

Processed images will be stored separately under:

```text
data/processed/
```

---

## 15. CLAHE Considerations

Contrast Limited Adaptive Histogram Equalization (CLAHE) may be used to improve retinal image contrast.

However, enhancement must be applied carefully.

Over-aggressive enhancement may introduce artificial intensity patterns or visual artifacts.

Therefore:

- CLAHE parameters must be documented.
- Original images must remain unchanged.
- Processed images must be stored separately.
- Enhanced images should be visually inspected.
- Model performance should be evaluated before and after enhancement where appropriate.

---

## 16. Image Quality Validation

Image quality is a core component of the NeuroVista-DR problem statement.

The dataset validation process should therefore identify potentially unsuitable images before they are used for model development.

### File-Level Checks

- File exists
- File can be opened
- File format is valid
- File is not corrupted

### Image-Level Checks

- Width
- Height
- Number of channels
- Pixel-value range
- Excessive darkness
- Excessive brightness
- Excessive blank regions

### Quality-Related Checks

Where annotations or suitable automated checks are available:

- Blur
- Focus
- Illumination
- Field of view
- Artifacts
- Retinal visibility

Poor-quality images should not automatically be treated as valid model inputs.

---

## 17. Dataset Metadata

Dataset metadata will be maintained separately from the original images.

The planned metadata structure is:

```text
data/
└── metadata/
    ├── dataset_inventory.csv
    ├── aptos_metadata.csv
    ├── idrid_metadata.csv
    └── validation_report.json
```

Potential metadata fields include:

```text
image_id
dataset
file_path
label
width
height
channels
format
quality_status
split
source
```

Only metadata supported by the corresponding dataset should be recorded.

No personally identifiable information should be added to project metadata.

---

## 18. Dataset Inventory

A dataset inventory will be maintained to track the state of each dataset.

The inventory should contain information such as:

| Field | Description |
|---|---|
| Dataset | Dataset name |
| Source | Original dataset source |
| Purpose | NeuroVista-DR role |
| Image Count | Number of available images |
| Labels | Available labels |
| Quality Annotations | Whether quality labels exist |
| Lesion Annotations | Whether lesion masks exist |
| Patient Information | Whether patient grouping is available |
| License | Dataset usage conditions |
| Status | Planned / Downloaded / Validated / Processed |

This inventory will make the dataset pipeline easier to reproduce and audit.

---

## 19. Raw Data Policy

The `data/raw/` directory is intended for original datasets obtained from their respective sources.

Raw data should not be modified.

If preprocessing is required, the processed output should be generated separately:

```text
data/
├── raw/
└── processed/
```

This preserves traceability between the original data and processed data.

Large datasets should not be committed to GitHub.

---

## 20. Processed Data Policy

Processed data should be generated programmatically whenever possible.

The preprocessing pipeline should document:

- Input dataset
- Input image
- Processing operations
- Resize dimensions
- Enhancement parameters
- Normalization method
- Processing version

This allows experiments to be reproduced without manually modifying individual images.

---

## 21. GitHub Data Policy

The GitHub repository should contain the code and documentation required to reproduce the dataset pipeline rather than large raw medical-image datasets.

The repository may contain:

- Dataset documentation
- Dataset metadata where permitted
- Validation scripts
- Preprocessing scripts
- Split-generation scripts
- Configuration files
- Reproducibility information

Raw or restricted datasets must not be committed unless their licensing and redistribution terms explicitly permit it.

Dataset-specific licenses and usage conditions must always be respected.

---

## 22. Data Source Tracking

Each dataset used by NeuroVista-DR should have its source and version recorded.

The project should track:

```text
Dataset Name
Official Source
Access Date
Dataset Version / Competition Version
License / Usage Terms
Expected Dataset Contents
Actual Dataset Contents
Validation Status
```

This information should be recorded in the dataset metadata or inventory.

---

## 23. Reproducibility

The dataset preparation pipeline should be reproducible by another team member.

The following should be documented where applicable:

- Dataset source
- Dataset version
- Download procedure
- Directory structure
- Preprocessing configuration
- Dataset split procedure
- Random seeds
- Validation procedure
- Python dependencies

Where randomized processing is used, fixed random seeds should be used for experiments where reproducibility is required.

---

## 24. Dataset Validation Pipeline

The planned validation workflow is:

```text
Dataset Download
       |
       v
File Inventory
       |
       v
Image Integrity Check
       |
       v
Metadata Validation
       |
       v
Label Validation
       |
       v
Duplicate Detection
       |
       v
Image Dimension Check
       |
       v
Class Distribution Analysis
       |
       v
Quality Analysis
       |
       v
Split Validation
       |
       v
Validation Report
```

The validation process will eventually generate a machine-readable report where practical.

---

## 25. Planned Validation Script

The initial dataset validation implementation will be located at:

```text
src/
└── data/
    └── validate_dataset.py
```

The script will progressively support checks including:

```text
✓ Dataset directory exists
✓ Expected image files detected
✓ Images can be opened
✓ Image dimensions detected
✓ Image channels detected
✓ Invalid/corrupted images identified
✓ Labels validated
✓ Missing metadata identified
✓ Duplicate files detected
✓ Dataset statistics generated
```

Additional checks may be added as the project progresses.

---

## 26. Clinical Label Strategy

The primary NeuroVista-DR DR classification task will use the five-level grading structure:

```text
0 -> No DR
1 -> Mild DR
2 -> Moderate DR
3 -> Severe DR
4 -> Proliferative DR
```

The original labels provided by each dataset must be preserved before any mapping or transformation.

If a dataset uses a different grading convention, the mapping must be explicitly documented.

Labels must not be silently converted.

---

## 27. Referable DR

For the SIH problem statement, referable DR is defined as:

```text
Grade 2 or higher
```

Therefore:

```text
Grade 0 ----+
Grade 1 ----+----> Non-Referable

Grade 2 ----+
Grade 3 ----+----> Referable
Grade 4 ----+
```

The binary referable/non-referable result will be derived from the five-class DR grading model.

The binary task will not replace the primary ICDR 0–4 classification task.

---

## 28. Explainability Dataset Strategy

The explainability component will use both model-based and lesion-based evidence where annotations are available.

The intended concept is:

```text
Fundus Image
      |
      +--------------------+
      |                    |
      v                    v
DR Classifier        Lesion Ground Truth
      |                    |
      v                    v
Grad-CAM              Lesion Regions
      |                    |
      +---------+----------+
                |
                v
      Explainability Analysis
```

IDRiD is particularly useful for this purpose because of its pixel-level lesion annotations.

Grad-CAM visualizations should be interpreted as model-attribution information rather than guaranteed proof that the highlighted region represents the correct clinical lesion.

---

## 29. Image Quality Gating

The intended NeuroVista-DR pipeline will place image-quality assessment before final DR prediction.

```text
Fundus Image
      |
      v
Image Quality Assessment
      |
 ┌────┴────┐
 |         |
Good      Poor
 |         |
 v         v
DR AI    Recapture /
 |        Quality Feedback
 v
ICDR 0–4
```

This approach is intended to reduce the risk of producing an apparently confident prediction from an image that is unsuitable for reliable analysis.

---

## 30. Future Dataset Expansion

Additional datasets may be considered after the initial pipeline has been validated.

Possible future datasets include:

- DDR
- Additional Indian retinal datasets
- Device-specific datasets
- Rural screening datasets
- Institution-specific datasets

Any new dataset must first be evaluated for:

- Licensing
- Annotation quality
- Label compatibility
- Patient overlap
- Image quality
- Population relevance
- Device diversity

---

## 31. Dataset Scope for the Initial Prototype

The initial prototype will prioritize the following:

```text
Priority 1
APTOS 2019 + IDRiD
        |
        v
Baseline DR Classification

Priority 2
DeepDRiD
        |
        v
Image Quality Assessment

Priority 3
EyePACS
        |
        v
Large-Scale / Robustness Experiments

Priority 4
Messidor-2
        |
        v
External Validation
```

This staged approach prevents unnecessary dataset complexity during the initial implementation.

---

## 32. What Will Not Be Done

The NeuroVista-DR prototype will avoid:

- Blindly combining all datasets
- Treating one dataset as representative of every population
- Using external validation data for repeated model tuning
- Reporting target metrics as achieved results
- Treating Grad-CAM as definitive clinical evidence
- Uploading large datasets directly to GitHub
- Ignoring image-quality problems
- Ignoring dataset-specific label definitions
- Creating image-level splits when patient-level separation is available
- Claiming clinical deployment readiness from prototype results alone

---

## 33. Issue #3 Deliverables

The `[DATA] Prepare and Validate Prototype DR Dataset` task will include:

### Documentation

- [x] Dataset strategy documented
- [x] Dataset roles defined
- [x] Dataset combination strategy defined
- [x] Leakage prevention strategy defined
- [x] Domain-shift considerations documented
- [x] Data-storage policy defined

### Directory Structure

- [x] `data/raw/`
- [x] `data/processed/`
- [x] `data/metadata/`
- [x] `data/splits/`
- [x] `src/data/`

### Validation Infrastructure

- [ ] Dataset validation script
- [ ] Image integrity checks
- [ ] Label validation
- [ ] Dataset statistics
- [ ] Duplicate detection
- [ ] Validation report

### Dataset Preparation

- [ ] APTOS 2019 available locally
- [ ] IDRiD available locally
- [ ] Dataset inventory generated
- [ ] Initial metadata generated
- [ ] Reproducible splits generated

---

## 34. Definition of Done

Issue #3 will be considered complete when:

1. The required prototype datasets are available locally.
2. The datasets can be read programmatically.
3. Invalid or corrupted images can be identified.
4. Labels can be loaded and validated.
5. Dataset statistics can be generated.
6. Duplicate-data checks have been performed where practical.
7. Dataset splits are explicitly defined.
8. Data leakage risks have been addressed.
9. Dataset metadata is documented.
10. The process is reproducible by another team member.
11. Large/raw datasets remain outside GitHub unless redistribution is explicitly permitted.
12. The resulting dataset structure is ready for the M1 baseline DR classifier.

---

## 35. Final Dataset Pipeline

The intended NeuroVista-DR dataset pipeline is:

```text
                    DATA SOURCES
                         |
          +--------------+--------------+
          |              |              |
        APTOS           IDRiD        DeepDRiD
          |              |              |
          +--------------+--------------+
                         |
                         v
                  DATA VALIDATION
                         |
                         v
                 METADATA GENERATION
                         |
                         v
                DUPLICATE / LEAKAGE
                       CHECK
                         |
                         v
                 DATASET SPLITTING
                         |
                         v
                   PREPROCESSING
                         |
                         v
                 MODEL DEVELOPMENT
                         |
                         v
                 EXPLAINABILITY
                         |
                         v
                    MODEL LOCK
                         |
                         v
                  EXTERNAL TEST
                    Messidor-2
                         |
                         v
                  FINAL EVALUATION
```

---

## 36. Status

**Milestone:** M1 — Core AI Pipeline

**Issue:** `[DATA] Prepare and Validate Prototype DR Dataset`

**Status:** Dataset strategy and directory structure defined. Dataset validation and preparation implementation is pending.

The dataset pipeline will be expanded incrementally as the corresponding AI components are implemented.

---

## Important Note

NeuroVista-DR is an SIH prototype and research project.

Performance targets specified in the SIH problem statement are development targets and must not be presented as achieved results until they have been experimentally demonstrated.

The system should be presented as an AI-assisted diabetic retinopathy screening prototype rather than an autonomous medical diagnosis system.
