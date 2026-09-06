"""
NeuroVista-DR Dataset Validation Utility

Validates retinal image datasets before they enter the
NeuroVista-DR preprocessing and model-development pipeline.

Current support:
- Image readability
- Image dimensions
- Channel count
- Invalid pixel values
- SHA-256 duplicate detection
- Dataset split detection
- APTOS disease-grade label validation
- IDRiD disease-grade label validation
- Missing/orphan labels
- Cross-split duplicate detection
- Conflicting labels among duplicate images

Usage:
    python src/data/validate_dataset.py --path data/raw/aptos/aptos2019-blindness-detection/train_images
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
}


# ---------------------------------------------------------------------------
# Generic image validation
# ---------------------------------------------------------------------------


def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def validate_image(file_path: Path) -> dict:
    """Validate one image and return its metadata."""

    result = {
        "path": str(file_path),
        "valid": False,
        "width": None,
        "height": None,
        "channels": None,
        "error": None,
        "sha256": None,
    }

    try:
        # Verify image integrity first.
        with Image.open(file_path) as image:
            image.verify()

        # Re-open after verify() because verify() invalidates the image object.
        with Image.open(file_path) as image:
            image = image.convert("RGB")
            array = np.asarray(image)

            result["width"] = image.width
            result["height"] = image.height
            result["channels"] = array.shape[2]

            if not np.isfinite(array).all():
                result["error"] = "Image contains invalid pixel values."
                return result

            if array.size == 0:
                result["error"] = "Image contains no pixel data."
                return result

        result["sha256"] = calculate_sha256(file_path)
        result["valid"] = True

    except Exception as exc:
        result["error"] = str(exc)

    return result


def find_images(dataset_path: Path) -> list[Path]:
    """Find supported image files recursively."""

    return sorted(
        path
        for path in dataset_path.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


# ---------------------------------------------------------------------------
# Dataset / split detection
# ---------------------------------------------------------------------------


def detect_split(file_path: Path) -> str:
    """
    Detect whether an image belongs to training or testing data.

    Supports the IDRiD directory naming convention and common
    train/test directory names used by other datasets.
    """

    path_parts = [part.lower() for part in file_path.parts]

    if "training set" in path_parts:
        return "training"

    if "testing set" in path_parts:
        return "testing"

    if "train_images" in path_parts or "train" in path_parts:
        return "training"

    if "test_images" in path_parts or "test" in path_parts:
        return "testing"

    return "unknown"


# ---------------------------------------------------------------------------
# APTOS support
# ---------------------------------------------------------------------------


def find_aptos_label_file(dataset_path: Path) -> Path | None:
    """
    Locate the APTOS training label CSV.

    Expected layouts include:
        dataset_path/train.csv
        dataset_path.parent/train.csv
        dataset_path.parent.parent/train.csv
    """

    candidates = [
        dataset_path / "train.csv",
        dataset_path.parent / "train.csv",
        dataset_path.parent.parent / "train.csv",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def load_aptos_labels(csv_path: Path) -> dict[str, int]:
    """Load APTOS image IDs and ICDR grades from train.csv."""

    labels = {}

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"No header row found in {csv_path.name}."
            )

        reader.fieldnames = [
            header.strip().lstrip("\ufeff")
            for header in reader.fieldnames
        ]

        required_columns = {"id_code", "diagnosis"}

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Unexpected columns in {csv_path.name}. "
                f"Missing: {sorted(missing_columns)}. "
                f"Found: {reader.fieldnames}"
            )

        for row in reader:
            normalized_row = {
                key.strip().lstrip("\ufeff"): (
                    value.strip() if value is not None else ""
                )
                for key, value in row.items()
            }

            image_id = normalized_row["id_code"]
            diagnosis = normalized_row["diagnosis"]

            if not image_id:
                raise ValueError(
                    "Encountered an empty image ID in APTOS labels."
                )

            try:
                grade = int(diagnosis)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid APTOS diagnosis for {image_id}: "
                    f"{diagnosis!r}"
                ) from exc

            labels[image_id] = grade

    return labels


def validate_aptos_labels(
    dataset_path: Path,
    images: list[Path],
) -> dict:
    """Validate APTOS labels against discovered images."""

    label_file = find_aptos_label_file(dataset_path)

    result = {
        "available": False,
        "label_file": None,
        "labels": {},
        "missing_labels": [],
        "orphan_labels": [],
        "invalid_grades": [],
        "duplicate_label_ids": [],
    }

    if label_file is None:
        return result

    result["available"] = True
    result["label_file"] = label_file

    # Read raw rows separately so duplicate CSV IDs can be detected.
    with label_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"No header row found in {label_file.name}."
            )

        reader.fieldnames = [
            header.strip().lstrip("\ufeff")
            for header in reader.fieldnames
        ]

        required_columns = {"id_code", "diagnosis"}
        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Unexpected columns in {label_file.name}. "
                f"Missing: {sorted(missing_columns)}. "
                f"Found: {reader.fieldnames}"
            )

        raw_ids = []

        for row in reader:
            image_id = (
                row.get("id_code", "") or ""
            ).strip()

            raw_ids.append(image_id)

    duplicate_ids = [
        image_id
        for image_id, count in Counter(raw_ids).items()
        if image_id and count > 1
    ]

    result["duplicate_label_ids"] = sorted(duplicate_ids)

    labels = load_aptos_labels(label_file)
    result["labels"] = labels

    image_index = build_image_index(images)
    all_image_ids = set(image_index)

    # Validate every discovered image has a label.
    for image_id in sorted(all_image_ids):
        if image_id not in labels:
            result["missing_labels"].append(image_id)

    # Validate every CSV label has an image.
    for image_id in sorted(labels):
        if image_id not in all_image_ids:
            result["orphan_labels"].append(image_id)

    # Validate ICDR grade range.
    for image_id, grade in sorted(labels.items()):
        if grade not in {0, 1, 2, 3, 4}:
            result["invalid_grades"].append(
                f"{image_id}: invalid diagnosis {grade}"
            )

    return result


def print_aptos_label_validation(label_result: dict) -> None:
    """Print APTOS label validation results."""

    print("\n" + "=" * 70)
    print("APTOS Label Validation")
    print("=" * 70)

    if not label_result["available"]:
        print("\nAPTOS train.csv was not found.")
        print("Label validation skipped.")
        return

    label_file = label_result["label_file"]
    labels = label_result["labels"]

    print(f"\nLabel file:          {label_file}")
    print(f"Total labels:       {len(labels)}")

    print(
        f"Images without labels: "
        f"{len(label_result['missing_labels'])}"
    )

    print(
        f"Orphan labels:         "
        f"{len(label_result['orphan_labels'])}"
    )

    print(
        f"Invalid grades:        "
        f"{len(label_result['invalid_grades'])}"
    )

    print(
        f"Duplicate label IDs:   "
        f"{len(label_result['duplicate_label_ids'])}"
    )

    distribution = Counter(labels.values())

    print("\nDiagnosis distribution:")

    for grade in range(5):
        print(
            f"  Grade {grade}: {distribution.get(grade, 0)}"
        )

    if label_result["missing_labels"]:
        print("\nMissing labels:")

        for image_id in label_result["missing_labels"]:
            print(f"  - {image_id}")

    if label_result["orphan_labels"]:
        print("\nOrphan labels:")

        for image_id in label_result["orphan_labels"]:
            print(f"  - {image_id}")

    if label_result["invalid_grades"]:
        print("\nInvalid grades:")

        for item in label_result["invalid_grades"]:
            print(f"  - {item}")

    if label_result["duplicate_label_ids"]:
        print("\nDuplicate label IDs:")

        for image_id in label_result["duplicate_label_ids"]:
            print(f"  - {image_id}")


# ---------------------------------------------------------------------------
# IDRiD support
# ---------------------------------------------------------------------------


def find_idrid_label_files(
    dataset_path: Path,
) -> tuple[Path | None, Path | None]:
    """Locate IDRiD disease-grading CSV files."""

    groundtruth_dir = (
        dataset_path
        / "B. Disease Grading"
        / "2. Groundtruths"
    )

    if not groundtruth_dir.exists():
        return None, None

    training_csv = None
    testing_csv = None

    for csv_file in groundtruth_dir.glob("*.csv"):
        name = csv_file.name.lower()

        if "training" in name:
            training_csv = csv_file

        elif "testing" in name:
            testing_csv = csv_file

    return training_csv, testing_csv


def load_idrid_labels(
    csv_path: Path,
) -> dict[str, dict[str, str]]:
    """Load IDRiD disease-grading labels."""

    labels = {}

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"No header row found in {csv_path.name}."
            )

        reader.fieldnames = [
            header.strip().lstrip("\ufeff")
            for header in reader.fieldnames
        ]

        required_columns = {
            "Image name",
            "Retinopathy grade",
            "Risk of macular edema",
        }

        missing_columns = (
            required_columns - set(reader.fieldnames)
        )

        if missing_columns:
            raise ValueError(
                f"Unexpected columns in {csv_path.name}. "
                f"Missing: {sorted(missing_columns)}. "
                f"Found: {reader.fieldnames}"
            )

        for row in reader:
            normalized_row = {
                key.strip().lstrip("\ufeff"): (
                    value.strip() if value is not None else ""
                )
                for key, value in row.items()
            }

            image_id = normalized_row["Image name"]

            labels[image_id] = {
                "retinopathy_grade": normalized_row[
                    "Retinopathy grade"
                ],
                "macular_edema_grade": normalized_row[
                    "Risk of macular edema"
                ],
            }

    return labels


def build_image_index(
    images: list[Path],
) -> dict[str, list[Path]]:
    """Map image IDs to physical files."""

    index = defaultdict(list)

    for image_path in images:
        image_id = image_path.stem
        index[image_id].append(image_path)

    return dict(index)


def validate_idrid_labels(
    dataset_path: Path,
    images: list[Path],
) -> dict:
    """Validate IDRiD disease-grading labels."""

    training_csv, testing_csv = find_idrid_label_files(
        dataset_path
    )

    result = {
        "available": False,
        "training_labels": {},
        "testing_labels": {},
        "missing_labels": [],
        "orphan_labels": [],
        "split_mismatches": [],
        "duplicate_label_conflicts": [],
    }

    if training_csv is None or testing_csv is None:
        return result

    result["available"] = True

    training_labels = load_idrid_labels(training_csv)
    testing_labels = load_idrid_labels(testing_csv)

    result["training_labels"] = training_labels
    result["testing_labels"] = testing_labels

    image_index = build_image_index(images)

    for image_id, image_paths in image_index.items():
        in_training = image_id in training_labels
        in_testing = image_id in testing_labels

        if not in_training and not in_testing:
            result["missing_labels"].append(image_id)

        for image_path in image_paths:
            actual_split = detect_split(image_path)

            if (
                actual_split == "training"
                and not in_training
            ):
                result["split_mismatches"].append(
                    f"{image_id}: image is in training "
                    f"directory but has no training label"
                )

            elif (
                actual_split == "testing"
                and not in_testing
            ):
                result["split_mismatches"].append(
                    f"{image_id}: image is in testing "
                    f"directory but has no testing label"
                )

    all_image_ids = set(image_index)

    for image_id in training_labels:
        if image_id not in all_image_ids:
            result["orphan_labels"].append(
                f"{image_id}: training label has "
                f"no corresponding image"
            )

    for image_id in testing_labels:
        if image_id not in all_image_ids:
            result["orphan_labels"].append(
                f"{image_id}: testing label has "
                f"no corresponding image"
            )

    return result


# ---------------------------------------------------------------------------
# Duplicate / leakage analysis
# ---------------------------------------------------------------------------


def analyze_duplicates(
    image_results: list[dict],
) -> dict[str, list[dict]]:
    """Group images with identical SHA-256 hashes."""

    groups = defaultdict(list)

    for result in image_results:
        if result["valid"] and result["sha256"]:
            groups[result["sha256"]].append(result)

    return {
        image_hash: entries
        for image_hash, entries in groups.items()
        if len(entries) > 1
    }


def print_duplicate_analysis(
    duplicate_groups: dict[str, list[dict]],
    label_result: dict,
    dataset_type: str,
) -> tuple[int, int]:
    """
    Print duplicate analysis.

    Returns:
        (cross_split_group_count, conflicting_label_group_count)
    """

    cross_split_groups = 0
    conflicting_label_groups = 0

    if not duplicate_groups:
        print("\nDuplicate analysis:")
        print("  No duplicate image files detected.")
        return 0, 0

    print("\nDuplicate analysis:")

    if dataset_type == "aptos":
        aptos_labels = label_result.get("labels", {})

    else:
        aptos_labels = {}

    training_labels = label_result.get(
        "training_labels",
        {},
    )

    testing_labels = label_result.get(
        "testing_labels",
        {},
    )

    for group_number, (
        image_hash,
        entries,
    ) in enumerate(
        duplicate_groups.items(),
        start=1,
    ):
        splits = {
            detect_split(Path(entry["path"]))
            for entry in entries
        }

        is_cross_split = (
            "training" in splits
            and "testing" in splits
        )

        if is_cross_split:
            cross_split_groups += 1

        print(f"\n  Duplicate group {group_number}")
        print(f"  SHA-256: {image_hash}")

        labels = []

        for entry in entries:
            image_path = Path(entry["path"])
            image_id = image_path.stem
            split = detect_split(image_path)

            if dataset_type == "aptos":
                label = aptos_labels.get(image_id)

                print(
                    f"    - {image_path.name} [{split}]"
                )

                if label is not None:
                    print(
                        f"      DR grade: {label}"
                    )
                    labels.append(label)

            else:
                if split == "training":
                    label = training_labels.get(
                        image_id
                    )

                elif split == "testing":
                    label = testing_labels.get(
                        image_id
                    )

                else:
                    label = (
                        training_labels.get(image_id)
                        or testing_labels.get(image_id)
                    )

                print(
                    f"    - {image_path.name} [{split}]"
                )

                if label:
                    print(
                        f"      DR grade: "
                        f"{label['retinopathy_grade']}, "
                        f"DME risk: "
                        f"{label['macular_edema_grade']}"
                    )

                    labels.append(
                        (
                            label["retinopathy_grade"],
                            label["macular_edema_grade"],
                        )
                    )

        if is_cross_split:
            print("      ⚠ CROSS-SPLIT DUPLICATE")

        if len(set(labels)) > 1:
            conflicting_label_groups += 1
            print("      ⚠ CONFLICTING LABELS")

    return cross_split_groups, conflicting_label_groups


# ---------------------------------------------------------------------------
# Dataset type detection
# ---------------------------------------------------------------------------


def detect_dataset_type(
    dataset_path: Path,
) -> str:
    """
    Detect the dataset type from its directory structure.

    Returns:
        "aptos"
        "idrid"
        "generic"
    """

    aptos_csv = find_aptos_label_file(dataset_path)

    if aptos_csv is not None:
        return "aptos"

    training_csv, testing_csv = find_idrid_label_files(
        dataset_path
    )

    if training_csv is not None and testing_csv is not None:
        return "idrid"

    path_text = str(dataset_path).lower()

    if "aptos" in path_text:
        return "aptos"

    if "idrid" in path_text:
        return "idrid"

    return "generic"


# ---------------------------------------------------------------------------
# Main validation pipeline
# ---------------------------------------------------------------------------


def validate_dataset(dataset_path: Path) -> None:
    """Run the complete dataset validation."""

    print("=" * 70)
    print("NeuroVista-DR Dataset Validation")
    print("=" * 70)

    print(
        f"\nDataset path: "
        f"{dataset_path.resolve()}"
    )

    if not dataset_path.exists():
        print("\nERROR: Dataset path does not exist.")
        return

    if not dataset_path.is_dir():
        print(
            "\nERROR: Dataset path is not a directory."
        )
        return

    dataset_type = detect_dataset_type(
        dataset_path
    )

    print(
        f"\nDetected dataset type: "
        f"{dataset_type.upper()}"
    )

    images = find_images(dataset_path)

    if not images:
        print(
            "\nWARNING: No supported image files found."
        )

        print(
            "Supported formats: "
            + ", ".join(
                sorted(SUPPORTED_EXTENSIONS)
            )
        )

        return

    print(
        f"\nImages discovered: {len(images)}"
    )

    print("\nValidating images...\n")

    valid_images = 0
    invalid_images = 0

    dimensions = Counter()
    channels = Counter()

    image_results = []
    errors = []

    for index, image_path in enumerate(
        images,
        start=1,
    ):
        result = validate_image(
            image_path
        )

        image_results.append(result)

        if result["valid"]:
            valid_images += 1

            dimensions[
                (
                    result["width"],
                    result["height"],
                )
            ] += 1

            channels[
                result["channels"]
            ] += 1

        else:
            invalid_images += 1

            errors.append(
                (
                    str(image_path),
                    result["error"]
                    or "Unknown error",
                )
            )

        print(
            f"\rProcessed "
            f"{index}/{len(images)} images",
            end="",
            flush=True,
        )

    print("\n")

    # ---------------------------------------------------------------
    # Image validation summary
    # ---------------------------------------------------------------

    print("=" * 70)
    print("Image Validation Summary")
    print("=" * 70)

    print(
        f"\nTotal images:       {len(images)}"
    )

    print(
        f"Valid images:       {valid_images}"
    )

    print(
        f"Invalid images:     {invalid_images}"
    )

    print("\nImage dimensions:")

    for dimension, count in dimensions.most_common():
        print(
            f"  {dimension[0]} x "
            f"{dimension[1]} : {count}"
        )

    print("\nChannel counts:")

    for channel_count, count in sorted(
        channels.items()
    ):
        print(
            f"  {channel_count} channel(s): "
            f"{count}"
        )

    if errors:
        print("\nInvalid images:")

        for image_path, error in errors:
            print(f"  - {image_path}")
            print(f"    Error: {error}")

    # ---------------------------------------------------------------
    # Dataset-specific label validation
    # ---------------------------------------------------------------

    label_result = {
        "available": False,
    }

    if dataset_type == "aptos":

        try:
            label_result = validate_aptos_labels(
                dataset_path,
                images,
            )

            print_aptos_label_validation(
                label_result
            )

        except Exception as exc:
            print(
                "\nERROR: Could not validate "
                "APTOS labels."
            )

            print(f"Reason: {exc}")
            return

    elif dataset_type == "idrid":

        print("\n" + "=" * 70)
        print("IDRiD Label Validation")
        print("=" * 70)

        try:
            label_result = validate_idrid_labels(
                dataset_path,
                images,
            )

        except Exception as exc:
            print(
                "\nERROR: Could not validate "
                "IDRiD labels."
            )

            print(f"Reason: {exc}")
            return

        if not label_result["available"]:
            print(
                "\nIDRiD disease-grading CSV "
                "files were not found."
            )

            print(
                "Label validation skipped."
            )

        else:
            training_labels = (
                label_result["training_labels"]
            )

            testing_labels = (
                label_result["testing_labels"]
            )

            print(
                f"\nTraining labels:    "
                f"{len(training_labels)}"
            )

            print(
                f"Testing labels:     "
                f"{len(testing_labels)}"
            )

            print(
                f"Total labels:       "
                f"{len(training_labels) + len(testing_labels)}"
            )

            print(
                f"\nImages without labels: "
                f"{len(label_result['missing_labels'])}"
            )

            print(
                f"Orphan labels:         "
                f"{len(label_result['orphan_labels'])}"
            )

            print(
                f"Split mismatches:      "
                f"{len(label_result['split_mismatches'])}"
            )

    else:
        print("\nDataset-specific label validation:")
        print("  No dataset-specific validator selected.")

    # ---------------------------------------------------------------
    # Duplicate validation
    # ---------------------------------------------------------------

    duplicate_groups = analyze_duplicates(
        image_results
    )

    print(
        f"\nDuplicate groups:   "
        f"{len(duplicate_groups)}"
    )

    # ---------------------------------------------------------------
    # Duplicate + leakage analysis
    # ---------------------------------------------------------------

    print("\n" + "=" * 70)
    print("Duplicate / Leakage Analysis")
    print("=" * 70)

    cross_split_groups, conflicting_label_groups = (
        print_duplicate_analysis(
            duplicate_groups,
            label_result,
            dataset_type,
        )
    )

    print(
        f"\nCross-split duplicate groups: "
        f"{cross_split_groups}"
    )

    print(
        f"Conflicting-label duplicate groups: "
        f"{conflicting_label_groups}"
    )

    # ---------------------------------------------------------------
    # Final result
    # ---------------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL VALIDATION RESULT")
    print("=" * 70)

    issues = []

    if invalid_images:
        issues.append(
            "invalid/unreadable images"
        )

    if duplicate_groups:
        issues.append(
            "duplicate image files"
        )

    if cross_split_groups:
        issues.append(
            "cross-split image leakage"
        )

    if conflicting_label_groups:
        issues.append(
            "conflicting labels among duplicates"
        )

    if dataset_type == "aptos" and label_result.get(
        "available"
    ):
        if label_result["missing_labels"]:
            issues.append(
                "missing APTOS labels"
            )

        if label_result["orphan_labels"]:
            issues.append(
                "orphan APTOS labels"
            )

        if label_result["invalid_grades"]:
            issues.append(
                "invalid APTOS grades"
            )

        if label_result["duplicate_label_ids"]:
            issues.append(
                "duplicate APTOS label IDs"
            )

    if dataset_type == "idrid" and label_result.get(
        "available"
    ):
        if label_result["missing_labels"]:
            issues.append(
                "missing labels"
            )

        if label_result["orphan_labels"]:
            issues.append(
                "orphan labels"
            )

        if label_result["split_mismatches"]:
            issues.append(
                "split mismatches"
            )

    if not issues:
        print("\nRESULT: PASS")
        print(
            "Dataset passed all implemented "
            "validation checks."
        )

    else:
        print(
            "\nRESULT: REVIEW REQUIRED"
        )

        print("\nDetected issues:")

        for issue in issues:
            print(f"  - {issue}")

    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate a NeuroVista-DR "
            "retinal image dataset."
        )
    )

    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help=(
            "Path to the dataset directory."
        ),
    )

    return parser.parse_args()


def main() -> None:
    """Program entry point."""

    args = parse_arguments()

    validate_dataset(
        args.path
    )


if __name__ == "__main__":
    main()