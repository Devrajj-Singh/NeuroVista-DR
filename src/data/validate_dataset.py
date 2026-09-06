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
- IDRiD disease-grade label validation
- Missing/orphan labels
- Cross-split duplicate detection
- Conflicting labels among duplicate images

Usage:
    python src/data/validate_dataset.py --path data/raw/IDRiD
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


def detect_split(file_path: Path) -> str:
    """Detect whether an image belongs to the training or testing directory."""
    path_text = str(file_path).lower()

    if "training set" in path_text:
        return "training"

    if "testing set" in path_text:
        return "testing"

    return "unknown"


def find_idrid_label_files(dataset_path: Path) -> tuple[Path | None, Path | None]:
    """Locate IDRiD disease-grading CSV files."""
    groundtruth_dir = dataset_path / "B. Disease Grading" / "2. Groundtruths"

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


def load_labels(csv_path: Path) -> dict[str, dict[str, str]]:
    """Load IDRiD disease-grading labels."""

    labels = {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        # Normalize CSV headers to remove accidental whitespace/BOM characters.
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

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Unexpected columns in {csv_path.name}. "
                f"Missing: {sorted(missing_columns)}. "
                f"Found: {reader.fieldnames}"
            )

        for row in reader:
            # Normalize row keys as well.
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


def build_image_index(images: list[Path]) -> dict[str, list[Path]]:
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
    """Validate IDRiD disease-grading labels against discovered images."""

    training_csv, testing_csv = find_idrid_label_files(dataset_path)

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

    training_labels = load_labels(training_csv)
    testing_labels = load_labels(testing_csv)

    result["training_labels"] = training_labels
    result["testing_labels"] = testing_labels

    image_index = build_image_index(images)

    # Validate every discovered image has a corresponding label.
    for image_id, image_paths in image_index.items():

        in_training = image_id in training_labels
        in_testing = image_id in testing_labels

        if not in_training and not in_testing:
            result["missing_labels"].append(image_id)

        # Check whether the physical directory agrees with the CSV split.
        for image_path in image_paths:
            actual_split = detect_split(image_path)

            if actual_split == "training" and not in_training:
                result["split_mismatches"].append(
                    f"{image_id}: image is in training directory but "
                    f"has no training label"
                )

            elif actual_split == "testing" and not in_testing:
                result["split_mismatches"].append(
                    f"{image_id}: image is in testing directory but "
                    f"has no testing label"
                )

    # Validate every CSV label has a corresponding image.
    all_image_ids = set(image_index)

    for image_id in training_labels:
        if image_id not in all_image_ids:
            result["orphan_labels"].append(
                f"{image_id}: training label has no corresponding image"
            )

    for image_id in testing_labels:
        if image_id not in all_image_ids:
            result["orphan_labels"].append(
                f"{image_id}: testing label has no corresponding image"
            )

    return result


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
) -> tuple[int, int]:
    """Print duplicate analysis and return group/conflict counts."""

    cross_split_groups = 0
    conflicting_label_groups = 0

    if not duplicate_groups:
        print("\nDuplicate analysis:")
        print("  No duplicate image files detected.")
        return 0, 0

    print("\nDuplicate analysis:")

    training_labels = label_result.get("training_labels", {})
    testing_labels = label_result.get("testing_labels", {})

    for group_number, (image_hash, entries) in enumerate(
        duplicate_groups.items(),
        start=1,
    ):
        splits = {detect_split(Path(entry["path"])) for entry in entries}

        is_cross_split = "training" in splits and "testing" in splits

        if is_cross_split:
            cross_split_groups += 1

        print(f"\n  Duplicate group {group_number}")
        print(f"  SHA-256: {image_hash}")

        labels = []

        for entry in entries:
            image_path = Path(entry["path"])
            image_id = image_path.stem
            split = detect_split(image_path)

            if split == "training":
                label = training_labels.get(image_id)

            elif split == "testing":
                label = testing_labels.get(image_id)

            else:
                label = training_labels.get(image_id) or testing_labels.get(image_id)

            print(f"    - {image_id}.jpg [{split}]")

            if label:
                print(
                    f"      DR grade: {label['retinopathy_grade']}, "
                    f"DME risk: {label['macular_edema_grade']}"
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


def validate_dataset(dataset_path: Path) -> None:
    """Run the complete dataset validation."""

    print("=" * 70)
    print("NeuroVista-DR Dataset Validation")
    print("=" * 70)

    print(f"\nDataset path: {dataset_path.resolve()}")

    if not dataset_path.exists():
        print("\nERROR: Dataset path does not exist.")
        return

    if not dataset_path.is_dir():
        print("\nERROR: Dataset path is not a directory.")
        return

    images = find_images(dataset_path)

    if not images:
        print("\nWARNING: No supported image files found.")
        print(
            "Supported formats: "
            + ", ".join(sorted(SUPPORTED_EXTENSIONS))
        )
        return

    print(f"\nImages discovered: {len(images)}")
    print("\nValidating images...\n")

    valid_images = 0
    invalid_images = 0

    dimensions = Counter()
    channels = Counter()

    image_results = []
    errors = []

    for index, image_path in enumerate(images, start=1):
        result = validate_image(image_path)

        image_results.append(result)

        if result["valid"]:
            valid_images += 1

            dimensions[
                (result["width"], result["height"])
            ] += 1

            channels[result["channels"]] += 1

        else:
            invalid_images += 1
            errors.append(
                (
                    str(image_path),
                    result["error"] or "Unknown error",
                )
            )

        print(
            f"\rProcessed {index}/{len(images)} images",
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

    print(f"\nTotal images:       {len(images)}")
    print(f"Valid images:       {valid_images}")
    print(f"Invalid images:     {invalid_images}")

    print("\nImage dimensions:")

    for dimension, count in dimensions.most_common():
        print(
            f"  {dimension[0]} x {dimension[1]} : {count}"
        )

    print("\nChannel counts:")

    for channel_count, count in sorted(channels.items()):
        print(
            f"  {channel_count} channel(s): {count}"
        )

    if errors:
        print("\nInvalid images:")

        for image_path, error in errors:
            print(f"  - {image_path}")
            print(f"    Error: {error}")

    # ---------------------------------------------------------------
    # Duplicate validation
    # ---------------------------------------------------------------

    duplicate_groups = analyze_duplicates(image_results)

    print(f"\nDuplicate groups:   {len(duplicate_groups)}")

    # ---------------------------------------------------------------
    # IDRiD label validation
    # ---------------------------------------------------------------

    print("\n" + "=" * 70)
    print("IDRiD Label Validation")
    print("=" * 70)

    try:
        label_result = validate_idrid_labels(
            dataset_path,
            images,
        )

    except Exception as exc:
        print(f"\nERROR: Could not validate IDRiD labels.")
        print(f"Reason: {exc}")
        return

    if not label_result["available"]:
        print("\nIDRiD disease-grading CSV files were not found.")
        print("Label validation skipped.")

    else:
        training_labels = label_result["training_labels"]
        testing_labels = label_result["testing_labels"]

        print(f"\nTraining labels:    {len(training_labels)}")
        print(f"Testing labels:     {len(testing_labels)}")
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

        if label_result["missing_labels"]:
            print("\nMissing labels:")

            for image_id in label_result["missing_labels"]:
                print(f"  - {image_id}")

        if label_result["orphan_labels"]:
            print("\nOrphan labels:")

            for item in label_result["orphan_labels"]:
                print(f"  - {item}")

        if label_result["split_mismatches"]:
            print("\nSplit mismatches:")

            for item in label_result["split_mismatches"]:
                print(f"  - {item}")

    # ---------------------------------------------------------------
    # Duplicate + label analysis
    # ---------------------------------------------------------------

    print("\n" + "=" * 70)
    print("Duplicate / Leakage Analysis")
    print("=" * 70)

    cross_split_groups, conflicting_label_groups = (
        print_duplicate_analysis(
            duplicate_groups,
            label_result,
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
        issues.append("invalid/unreadable images")

    if duplicate_groups:
        issues.append("duplicate image files")

    if cross_split_groups:
        issues.append("cross-split image leakage")

    if conflicting_label_groups:
        issues.append("conflicting labels among duplicates")

    if label_result["available"]:
        if label_result["missing_labels"]:
            issues.append("missing labels")

        if label_result["orphan_labels"]:
            issues.append("orphan labels")

        if label_result["split_mismatches"]:
            issues.append("split mismatches")

    if not issues:
        print("\nRESULT: PASS")
        print("Dataset passed all implemented validation checks.")

    else:
        print("\nRESULT: REVIEW REQUIRED")
        print("\nDetected issues:")

        for issue in issues:
            print(f"  - {issue}")

    print("=" * 70)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Validate a NeuroVista-DR retinal image dataset."
    )

    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to the dataset directory.",
    )

    return parser.parse_args()


def main() -> None:
    """Program entry point."""

    args = parse_arguments()
    validate_dataset(args.path)


if __name__ == "__main__":
    main()