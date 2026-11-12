# Multi-Dataset Training and Evaluation Protocol

## 1. Purpose and status

This protocol fixes the dataset roles, split boundaries, model-selection rules,
and reporting requirements for ICDR diabetic retinopathy (DR) grading before
full-scale training. It is a prospective protocol, not a report of completed
training or clinical validation. No performance target in this document is an
achieved result.

The protocol is based on the audited dataset roles in
[`dataset-strategy.md`](dataset-strategy.md) and the existing baseline in
[`baseline-classification.md`](baseline-classification.md). It does not claim
that unavailable raw data or a unified loader has been implemented. In this
checkout, metadata and split manifests are present, but `data/raw/` is absent;
the classifier loader in `src/ai/classification/dataset.py` is APTOS-specific,
and the current APTOS and IDRiD project splits do not provide a final test
partition. These gaps must be addressed before the protocol is used for full
training.

This protocol is framework-agnostic and does not change the repository
requirement that the final AI core pipeline genuinely execute through MATLAB,
as stated in `baseline-classification.md`. References to the current Python
baseline describe existing development code, not a change to that
requirement.

## 2. Task and label policy

The primary classification task is five-class ICDR grading:

| Label | Grade |
|---:|---|
| 0 | No DR |
| 1 | Mild NPDR |
| 2 | Moderate NPDR |
| 3 | Severe NPDR |
| 4 | Proliferative DR |

**Referable DR is fixed as ICDR grade >= 2.** Preserve each dataset's original
labels in its metadata. Apply a documented mapping only after verifying that
the source grading definitions are compatible with ICDR 0–4.

For IDRiD, use `retinopathy_grade` as the image-level DR classification label.
Keep macular-edema grades, lesion masks, and optic-disc/fovea annotations as
separate targets or annotation references. Do not merge lesion or macular
edema labels into the DR grade, use them as classification inputs, or treat
pixel annotations as image-level grading labels.

## 3. Dataset roles and split policy

| Dataset | Role in this protocol | Split and use policy |
|---|---|---|
| APTOS 2019 | Primary ICDR grading development and internal evaluation; primary baseline training source. | After integrity checks and duplicate handling, create a fixed, label-stratified split of 70% training, 10% model-selection validation, 5% calibration/threshold selection, and 15% untouched internal test. Freeze the resulting manifest before training. |
| IDRiD | Indian-domain grading evaluation, lesion/evidence work, and a separately reported source for a pre-specified multi-source training experiment. | Preserve the verified official training/testing assignment. Use only unique, valid records from the official training portion for fitting; allocate 85% of that portion to training, 10% to model-selection validation, and 5% to calibration/threshold selection. Keep the clean official testing portion untouched and never move its records into development. An APTOS-only model may use that clean testing portion for cross-dataset evaluation, but its results must not inform development. For a pooled model that trains or calibrates on IDRiD, report the official testing portion as a locked IDRiD holdout, not as independent external validation. |
| DeepDRiD | Image-quality assessment and quality-gating, if obtained and verified. | Keep its quality task separate from ICDR grading. Group by patient for its quality-model splits. Use it for DR grading only in a separately specified experiment after label compatibility and provenance are verified. |
| EyePACS | Optional large-scale pretraining or robustness experiments, if obtained and verified. | Do not automatically mix it into supervised ICDR training. Audit label definitions and patient identifiers first; if used, patient-group its development splits and keep a locked evaluation partition. |
| Messidor-2 | External validation only, if obtained and verified. | Keep the dataset wholly outside fitting, model/architecture selection, threshold selection, calibration, and iterative development. Evaluate only a frozen model and frozen operating point, and report it separately from internal tests. |

The percentages above are protocol allocations, not descriptions of the
existing manifests. For APTOS, generate a new manifest with all four roles;
the current `data/splits/aptos_split.csv` has train, validation, and excluded
duplicate records, but no test or calibration partition. For IDRiD, retain the
source split in `data/metadata/idrid_manifest.csv` when verifying and
constructing the protocol split. Do not treat
`data/metadata/idrid_project_split.csv` as an untouched test split: it is a
project train/validation split.

Use **random seed 42** for split generation and calibration cross-fitting,
consistent with the existing APTOS and IDRiD split scripts and the classifier
baseline. Use deterministic, label-stratified group assignment; keep patient
groups intact where identifiers exist, and exact-duplicate groups intact for
exclusion. The clean eligible population, exact counts, class support,
exclusions, seed, split-generation code/version, and split-manifest hash must
be recorded when the manifests are generated. Reuse the frozen manifest rather
than regenerating it for subsequent runs. If a class or patient group makes
the proposed allocation impractical, document the reason and the revised
allocation before training; do not rebalance or change a split in response to
test results.

## 4. Patient separation, duplicates, and leakage controls

1. Validate image files, labels, source provenance, and annotation links before
   splitting. Do not include an image that cannot be resolved and opened.
2. Where a verified patient identifier exists, assign all images from that
   patient to one partition. Keep both eyes and repeat visits together when
   those relationships are available.
3. The current APTOS and IDRiD split manifests do not contain a `patient_id`
   field. Patient-level separation therefore cannot be claimed from those
   manifests. Check source metadata for a usable identifier; if none is
   available, split by image after duplicate grouping and state this limitation
   in every relevant report.
4. Compute exact content hashes across all datasets before splitting. Exclude
   exact-duplicate groups from the clean eligible population, consistent with
   the existing APTOS and IDRiD split-generation policies. In particular, if
   an IDRiD duplicate group spans its official training and testing portions,
   exclude every record in that group; do not move an official testing record
   into development or leave another copy in the test set. Exclude
   cross-dataset duplicate groups from all protocol partitions. Record the
   excluded records and reasons. No matching content may cross training,
   validation, calibration, or test.
5. Run near-duplicate screening (for example, perceptual hashes or image
   similarity review) across and within datasets before finalizing splits.
   Record reviewed matches and their disposition. A near-duplicate group must
   not cross a development/test boundary.
6. Apply augmentation only to training samples, after partition assignment.
   Validation, calibration, and test preprocessing must be deterministic.
   Keep caches partition-specific and never derive preprocessing statistics
   from calibration, test, or external-validation images.
7. Keep each dataset's source identity in the unified metadata and report
   dataset-wise results. A cross-dataset duplicate check is required before
   describing an evaluation as cross-dataset.

## 5. Model selection and locked evaluation

- Fit model weights on training partitions only. Use the model-selection
  validation partition for checkpoint selection, hyperparameter comparison,
  and architecture decisions. For the existing baseline, checkpoint selection
  remains minimum validation loss, consistent with `train.py`. Compare
  candidate model configurations by macro F1 on the model-selection
  validation partition; for a multi-source model, use the unweighted mean of
  the per-dataset macro F1 values so each source has equal influence. Break
  ties using the lower validation loss (the unweighted mean of per-dataset
  losses for multi-source models). Report macro F1 and per-class performance
  alongside the selection metric.
- For a multi-source model, include only the designated training partitions.
  Evaluate validation performance by dataset; use a predeclared
  dataset-balanced aggregate for model comparison so a larger dataset does not
  silently dominate. Do not select or reject a model based on test results.
- Use the calibration/threshold partition only after a candidate model is
  selected. Do not use it to fit model weights or select epochs.
- Freeze the model, preprocessing, class mapping, calibration method, and
  decision threshold before opening final test predictions or labels. Run the
  internal and external final evaluations once for the frozen experiment and
  retain the outputs. If results are used to make another development
  decision, treat that evaluation set as consumed; a new untouched test source
  or partition is then required.
- Pre-specify any candidate-model comparisons before evaluating test sets. Do
  not use the test set to choose the winning model, threshold, calibration, or
  preprocessing.

## 6. Referable threshold and calibration

The **label rule** remains grade >= 2. After model selection, fit probability
calibration (temperature scaling for the five-class logits when calibrated
probabilities are required) using only the calibration/threshold partition.
Do not fit calibration parameters or choose the threshold using model-selection
validation or test data.

To avoid choosing a threshold on the same fitted calibration predictions,
generate out-of-fold calibrated scores within the calibration/threshold
partition using deterministic, label-stratified, five-fold cross-fitting.
Keep patient groups together where identifiers exist; otherwise keep
duplicate groups together. For each fold, fit the calibrator on the other
folds and predict the held-out fold. Select the binary operating threshold
from the concatenated held-out predictions, then fit the final calibrator on
the full calibration/threshold partition. If class or group counts do not
support five folds, use the largest feasible fold count of at least two and
record it; if fewer than two are feasible, do not tune a threshold from that
partition.

For an APTOS-only model, use its calibration partition to fit the calibrator
and select the threshold; apply those frozen values unchanged to IDRiD
cross-dataset evaluation. For a pre-specified multi-source model, use the
designated calibration partitions for each training source, with equal
dataset weighting for calibration fitting and threshold selection. Do not
use an IDRiD or other evaluation-only dataset's labels for this purpose.

Compute the referable score as the sum of calibrated predicted probabilities
for grades 2, 3, and 4. Select the threshold according to a predeclared
operating criterion: maximize specificity subject to sensitivity **greater
than 90%** on the cross-fitted calibration predictions. Include the
all-positive decision among candidate thresholds so this sensitivity
constraint is attainable whenever positive calibration examples are present.
If the calibration partition lacks either referable class, or the data cannot
support at least two valid folds, do not tune a probability threshold; obtain
adequate development calibration data before using a probability-based
operating point. Never choose a fallback based on test results. Record the
criterion, chosen threshold (if estimable), folds, and calibration support.
The SIH sensitivity and specificity targets are goals, not guaranteed
outcomes.

Freeze the final calibration parameters and threshold before test evaluation.
Apply the same frozen values to internal and cross-dataset tests; do not tune a
separate threshold on each test dataset. If source-specific calibration is
studied, it is a separate, pre-specified experiment using development
calibration data from that source, never its test data.

Raw softmax outputs are scores, not calibrated clinical probabilities. Do not
describe them as calibrated confidence unless calibration has been fitted and
evaluated on data separate from model fitting and final testing.

## 7. Evaluation metrics and reporting

Report metrics on the locked internal test and each external/cross-dataset
evaluation separately. Call an evaluation external/cross-dataset only when
that dataset was excluded from fitting, model selection, calibration, and
threshold selection. If a dataset contributed to any of those development
steps, report its held-out partition as an in-source test, not as external
validation. Include sample counts, class support, exclusions, and the frozen
model/threshold identifier.

### ICDR 0–4

- Confusion matrix with labels 0–4.
- Macro F1 and per-class precision, recall, and F1.
- Balanced accuracy (macro recall), and overall accuracy as a secondary
  summary.

### Referable DR (grade >= 2)

- Sensitivity, specificity, precision, F1, and binary confusion matrix at the
  frozen operating threshold.
- ROC-AUC and PR-AUC from continuous referable scores where both outcome
  classes are represented. State when a metric is not estimable.

### Confidence and calibration

- Multiclass negative log-likelihood and Brier score.
- For referable DR, binary Brier score and negative log-likelihood.
- Top-label multiclass ECE and binary referable ECE, each using 15 fixed,
  equal-width confidence bins over [0, 1] (empty bins are omitted), plus
  reliability plots where available.
- Report discrimination metrics separately from calibration metrics. Include
  calibration method and fitted parameters; do not substitute mean/max
  softmax confidence for calibration evaluation.

### Dataset and subgroup reporting

Provide dataset-wise metrics before any aggregate. Where sample support
permits, report performance by ICDR grade, camera/acquisition domain, and
available, appropriately governed demographic or image-quality subgroups.
Do not infer missing demographic or patient attributes. Report subgroup
support, missingness, and uncertainty. Provide confidence intervals, using
patient-level resampling when patient IDs are available and image-level
resampling otherwise; label the latter limitation.

## 8. Reproducibility record

For each experiment, save or document:

- Dataset name, source/version, provenance/license, verified files, label
  mapping, exclusions, and exact/near-duplicate review outcomes.
- Immutable split-manifest paths and hashes, split-generation code/version,
  fixed split/cross-fitting seed (42), grouping identifier used, counts, and
  per-split class distributions.
- Loader and preprocessing versions/configuration, image size, normalization,
  deterministic evaluation transforms, and training-only augmentation.
- Model architecture/initialization, loss, optimizer, learning-rate schedule,
  class-imbalance handling, random seeds, checkpoint-selection metric, and
  selected epoch.
- Runtime environment, framework/library versions, hardware/device, and
  experiment/code revision.
- Calibration method and fitted parameters, the referable-score definition,
  cross-fitting fold count, selected operating threshold and criterion, and
  frozen model identifier.
- Test predictions and probabilities, metric code/version, reporting
  subgroup definitions, and evaluation date.

Store metadata and results without committing restricted raw dataset images.
Never overwrite an existing split, checkpoint, or result in place; version
changed artifacts so the experiment remains auditable.
