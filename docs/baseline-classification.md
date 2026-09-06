# NeuroVista-DR — Baseline ICDR Classification

## 1. Purpose

This document defines the baseline deep-learning experiment for diabetic
retinopathy (DR) severity classification in NeuroVista-DR.

The objective is to establish a reproducible baseline capable of classifying
retinal fundus images into the five International Clinical Diabetic Retinopathy
(ICDR) severity levels.

This baseline is the foundation for later explainability, calibration,
lesion-level analysis, and application integration.

---

## 2. Classification Task

The model performs five-class diabetic retinopathy severity classification.

| Class | ICDR Level | Description |
|---:|---|---|
| 0 | No DR | No apparent diabetic retinopathy |
| 1 | Mild NPDR | Mild non-proliferative diabetic retinopathy |
| 2 | Moderate NPDR | Moderate non-proliferative diabetic retinopathy |
| 3 | Severe NPDR | Severe non-proliferative diabetic retinopathy |
| 4 | PDR | Proliferative diabetic retinopathy |

The primary model output is therefore one of five classes: 0, 1, 2, 3, or 4.

---

## 3. Baseline Model

### Backbone

EfficientNet-B0 will be used as the initial classification backbone.

The model will use transfer learning rather than training the complete
network from random initialization.

### Output Layer

The classification head will produce five output logits corresponding to
ICDR classes 0–4.

A softmax layer will convert logits into class probabilities for inference.

Raw softmax scores will not be described as clinically calibrated
probabilities until a dedicated calibration stage is implemented.

---

## 4. Dataset Strategy

The baseline grading experiment will initially use the prepared APTOS 2019
dataset as the primary development dataset.

IDRiD is retained as an important Indian retinal dataset and will be used
according to the project's dataset strategy rather than indiscriminately
combining all available datasets into the baseline.

The prepared IDRiD project split contains:

- 404 training images
- 100 validation images
- 504 unique image contents
- 12 duplicate records excluded from development

The IDRiD dataset will not be used as an additional source of training images
unless explicitly defined by a later experiment.

---

## 5. Data Leakage Policy

No image or identical image content may appear in both training and
validation sets.

Dataset duplicates are identified using SHA-256 image hashes during dataset
validation.

Patient-level separation will be preferred whenever patient identifiers are
available.

No validation image may be used for model fitting, augmentation statistics,
hyperparameter tuning based on repeated evaluation, or checkpoint selection
outside the defined validation procedure.

External datasets will remain separate from model-development data when used
for external evaluation.

---

## 6. Image Preprocessing

Fundus images will be converted to a consistent RGB representation and
resized to the input resolution required by the selected EfficientNet-B0
implementation.

The preprocessing pipeline will be kept deterministic for validation images.

Initial preprocessing may include:

- RGB normalization
- resizing
- fundus-region cropping where appropriate
- removal of unnecessary image borders

Image enhancement will be kept conservative in the baseline experiment.

Advanced image-quality assessment and adaptive enhancement belong to later
pipeline stages.

---

## 7. Data Augmentation

Training images may use moderate augmentation to improve robustness to
variation in image acquisition.

Initial augmentation candidates include:

- horizontal flipping
- small rotations
- limited scaling
- limited translation
- moderate brightness variation
- moderate contrast variation

Augmentation must not alter the clinical meaning of the retinal image.

Validation images will not use random augmentation.

---

## 8. Class Imbalance

DR datasets are typically imbalanced across severity levels.

The baseline experiment will first measure the class distribution before
training.

Class-imbalance handling will be selected based on the observed distribution.

Possible approaches include:

- class-weighted cross-entropy
- balanced sampling
- other documented weighting strategies

The selected strategy must be recorded with the experiment results.

---

## 9. Training Configuration

The initial training configuration will use:

| Parameter | Baseline |
|---|---|
| Task | 5-class ICDR classification |
| Backbone | EfficientNet-B0 |
| Learning strategy | Transfer learning |
| Loss | Cross-entropy |
| Optimizer | Adam |
| Validation | Fixed validation split |
| Checkpoint selection | Best validation performance |
| Random seed | Fixed and recorded |
| Precision | Standard initially |

The exact learning rate, batch size, number of epochs, and scheduler will be
recorded with the implementation and experiment results rather than silently
changing during training.

---

## 10. Evaluation Metrics

The baseline will report:

### Multiclass metrics

- Overall accuracy
- Macro precision
- Macro recall
- Macro F1-score
- Per-class precision
- Per-class recall
- Per-class F1-score
- Confusion matrix

Macro-averaged metrics are important because overall accuracy can hide poor
performance on minority DR severity classes.

### Referable DR

For the SIH problem, referable DR is defined as:

> ICDR Grade >= 2

The five-class predictions will therefore also be converted into a binary
referable/non-referable outcome.

The following metrics will be calculated:

- Sensitivity
- Specificity
- Precision
- F1-score
- Confusion matrix

The SIH target of greater than 90% sensitivity and greater than 85%
specificity is a project target, not an assumed or achieved result.

---

## 11. Validation Procedure

The validation dataset will remain unseen during model parameter fitting.

The validation set will be used for:

- checkpoint selection
- model comparison
- baseline performance measurement

Repeated experimentation must be documented to avoid unintentionally
overfitting decisions to the validation set.

A separate external dataset will be required for a stronger assessment of
generalization.

---

## 12. Model Checkpoints

The trained model will be saved as a reproducible checkpoint.

The repository will not track large model artifacts directly unless
explicitly required.

Model files should remain excluded through `.gitignore` and their location,
format, training configuration, and experiment identifier should be
documented.

---

## 13. Reproducibility

Each baseline experiment should record:

- random seed
- dataset version
- dataset split
- preprocessing configuration
- augmentation configuration
- model architecture
- optimizer
- learning rate
- batch size
- number of epochs
- loss function
- class-imbalance strategy
- training environment
- MATLAB version
- relevant MATLAB toolboxes

The goal is to make the experiment reproducible rather than dependent on
undocumented local settings.

---

## 14. MATLAB Architecture Requirement

PS 26038 requires a MATLAB-based retinal image analysis pipeline.

MATLAB therefore remains the core environment for the final AI pipeline.

The project uses:

- MATLAB
- Deep Learning Toolbox
- Image Processing Toolbox
- Computer Vision Toolbox
- Statistics and Machine Learning Toolbox

Python may support dataset preparation, experimentation, validation, and
auxiliary tooling.

Python must not replace the required MATLAB core pipeline in the final
solution.

---

## 15. Baseline Scope

This issue covers only the baseline ICDR classification model.

### Included

- Dataset loading
- Image preprocessing
- Training augmentation
- EfficientNet-B0 transfer learning
- Five-class ICDR classification
- Model training
- Validation
- Multiclass evaluation
- Referable DR evaluation
- Checkpoint generation
- Reproducibility documentation

### Not included

- Image-quality classification
- Automatic image rejection
- Grad-CAM
- Lesion segmentation
- Lesion-level evidence
- Confidence calibration
- FastAPI integration
- React dashboard
- Simulink workflow simulation
- Ophthalmologist review interface

These components will be implemented in subsequent issues.

---

## 16. Limitations

The baseline model is a development-stage machine-learning experiment.

Its results must not be interpreted as clinical validation or as evidence
that the system is ready for autonomous diagnosis.

Performance on one dataset does not establish generalization to all retinal
cameras, populations, acquisition conditions, or clinical settings.

External validation and prospective clinical evaluation remain necessary.

---

## 17. Definition of Done

- [ ] Baseline ICDR 0–4 classification pipeline implemented
- [ ] EfficientNet-B0 transfer-learning model configured
- [ ] Dataset loading implemented
- [ ] Image preprocessing implemented
- [ ] Training augmentation implemented
- [ ] Class distribution measured
- [ ] Class-imbalance strategy documented
- [ ] Model trained successfully
- [ ] Validation evaluation completed
- [ ] Confusion matrix generated
- [ ] Per-class metrics calculated
- [ ] Referable DR (ICDR >= 2) sensitivity calculated
- [ ] Referable DR (ICDR >= 2) specificity calculated
- [ ] Model checkpoint generated
- [ ] Inference verified on unseen validation images
- [ ] Reproducibility information recorded
- [ ] Results documented without overstating clinical performance

---

## 18. Expected Output

The completed issue should produce:

1. A working EfficientNet-B0 ICDR 0–4 classifier.
2. A reproducible training pipeline.
3. A validation evaluation pipeline.
4. Multiclass performance metrics.
5. Referable DR sensitivity and specificity.
6. A confusion matrix.
7. A saved model checkpoint.
8. Documented experiment configuration.

The resulting baseline will serve as the classification foundation for the
later NeuroVista-DR explainability and clinical-review workflow.