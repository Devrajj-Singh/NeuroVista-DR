"""
Generate a duplicate-safe train/validation split for APTOS 2019.

Input:
    data/metadata/aptos_metadata.csv

Output:
    data/splits/aptos_split.csv

Policy:
    - Raw APTOS images are never modified.
    - Every exact SHA-256 duplicate group is excluded.
    - Unique images are split into train/validation.
    - Stratification is performed by ICDR diagnosis.
    - The split is deterministic through a fixed random seed.
    - No image content can appear in both train and validation.

Usage:
    python data/splits/generate_aptos_split.py
"""

from __future__ import annotations

import csv
import random
from collections import Counter, defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "aptos_metadata.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "splits"
    / "aptos_split.csv"
)

# ---------------------------------------------------------------------------
# Split configuration
# ---------------------------------------------------------------------------

VALIDATION_RATIO = 0.20
RANDOM_SEED = 42


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------


def load_manifest() -> list[dict]:
    """Load the APTOS metadata manifest."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"APTOS manifest not found:\n{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                "APTOS metadata CSV has no header."
            )

        required_columns = {
            "image_id",
            "filename",
            "relative_path",
            "sha256",
            "diagnosis",
            "duplicate_group",
            "is_duplicate",
            "duplicate_status",
        }

        missing_columns = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing_columns:
            raise ValueError(
                "APTOS metadata is missing columns: "
                + ", ".join(sorted(missing_columns))
            )

        records = list(reader)

    return records


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_manifest(records: list[dict]) -> None:
    """Validate basic manifest integrity."""

    if not records:
        raise ValueError(
            "APTOS manifest contains no records."
        )

    image_ids = [
        record["image_id"]
        for record in records
    ]

    if len(image_ids) != len(set(image_ids)):
        raise ValueError(
            "Duplicate image IDs found in manifest."
        )

    for record in records:

        diagnosis = record["diagnosis"]

        if diagnosis == "":
            raise ValueError(
                f"Missing diagnosis for "
                f"{record['image_id']}."
            )

        try:
            diagnosis_int = int(diagnosis)
        except ValueError as exc:
            raise ValueError(
                f"Invalid diagnosis for "
                f"{record['image_id']}: {diagnosis}"
            ) from exc

        if diagnosis_int not in {0, 1, 2, 3, 4}:
            raise ValueError(
                f"Diagnosis outside ICDR 0–4 for "
                f"{record['image_id']}: "
                f"{diagnosis_int}"
            )

        if not record["sha256"]:
            raise ValueError(
                f"Missing SHA-256 for "
                f"{record['image_id']}."
            )


# ---------------------------------------------------------------------------
# Duplicate grouping
# ---------------------------------------------------------------------------


def group_by_hash(
    records: list[dict],
) -> dict[str, list[dict]]:
    """Group records by SHA-256 hash."""

    groups = defaultdict(list)

    for record in records:
        groups[record["sha256"]].append(record)

    return dict(groups)


def identify_excluded_records(
    records: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Separate unique records from duplicate records.

    Every exact duplicate group is excluded from the
    clean model-development population.
    """

    hash_groups = group_by_hash(records)

    development_records = []
    excluded_records = []

    for image_hash, group in hash_groups.items():

        if len(group) == 1:
            development_records.append(
                group[0]
            )

        else:
            excluded_records.extend(group)

    return (
        development_records,
        excluded_records,
    )


# ---------------------------------------------------------------------------
# Stratified deterministic split
# ---------------------------------------------------------------------------


def stratified_split(
    records: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Create a deterministic stratified train/validation split.

    Stratification is performed using ICDR diagnosis.
    """

    rng = random.Random(
        RANDOM_SEED
    )

    by_grade = defaultdict(list)

    for record in records:

        grade = int(
            record["diagnosis"]
        )

        by_grade[grade].append(
            record
        )

    train_records = []
    validation_records = []

    for grade in sorted(by_grade):

        grade_records = by_grade[grade].copy()

        # Deterministic shuffle.
        rng.shuffle(
            grade_records
        )

        validation_count = round(
            len(grade_records)
            * VALIDATION_RATIO
        )

        # Ensure classes with at least two samples
        # have at least one validation image.
        if (
            len(grade_records) >= 2
            and validation_count == 0
        ):
            validation_count = 1

        # Never place every image of a class
        # into validation.
        if validation_count >= len(
            grade_records
        ):
            validation_count = (
                len(grade_records) - 1
            )

        validation_records.extend(
            grade_records[
                :validation_count
            ]
        )

        train_records.extend(
            grade_records[
                validation_count:
            ]
        )

    # Final deterministic ordering.
    train_records.sort(
        key=lambda record: record["image_id"]
    )

    validation_records.sort(
        key=lambda record: record["image_id"]
    )

    return (
        train_records,
        validation_records,
    )


# ---------------------------------------------------------------------------
# Leakage verification
# ---------------------------------------------------------------------------


def verify_no_duplicate_leakage(
    train_records: list[dict],
    validation_records: list[dict],
) -> None:
    """Verify no identical image content crosses the split."""

    train_hashes = {
        record["sha256"]
        for record in train_records
    }

    validation_hashes = {
        record["sha256"]
        for record in validation_records
    }

    overlap = (
        train_hashes
        & validation_hashes
    )

    if overlap:
        raise RuntimeError(
            "Duplicate leakage detected! "
            f"{len(overlap)} SHA-256 hashes "
            "appear in both train and validation."
        )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_split(
    train_records: list[dict],
    validation_records: list[dict],
    excluded_records: list[dict],
) -> None:
    """Write the reproducible split CSV."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "image_id",
        "filename",
        "relative_path",
        "sha256",
        "diagnosis",
        "split",
        "duplicate_group",
        "duplicate_status",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in train_records:

            writer.writerow(
                {
                    "image_id": record["image_id"],
                    "filename": record["filename"],
                    "relative_path": record[
                        "relative_path"
                    ],
                    "sha256": record["sha256"],
                    "diagnosis": record["diagnosis"],
                    "split": "train",
                    "duplicate_group": record[
                        "duplicate_group"
                    ],
                    "duplicate_status": record[
                        "duplicate_status"
                    ],
                }
            )

        for record in validation_records:

            writer.writerow(
                {
                    "image_id": record["image_id"],
                    "filename": record["filename"],
                    "relative_path": record[
                        "relative_path"
                    ],
                    "sha256": record["sha256"],
                    "diagnosis": record["diagnosis"],
                    "split": "validation",
                    "duplicate_group": record[
                        "duplicate_group"
                    ],
                    "duplicate_status": record[
                        "duplicate_status"
                    ],
                }
            )

        for record in excluded_records:

            writer.writerow(
                {
                    "image_id": record["image_id"],
                    "filename": record["filename"],
                    "relative_path": record[
                        "relative_path"
                    ],
                    "sha256": record["sha256"],
                    "diagnosis": record["diagnosis"],
                    "split": "excluded_duplicate",
                    "duplicate_group": record[
                        "duplicate_group"
                    ],
                    "duplicate_status": record[
                        "duplicate_status"
                    ],
                }
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Generate the APTOS split."""

    print("=" * 70)
    print("APTOS Reproducible Split Generator")
    print("=" * 70)

    records = load_manifest()

    print(
        f"\nManifest records: {len(records)}"
    )

    validate_manifest(
        records
    )

    (
        development_records,
        excluded_records,
    ) = identify_excluded_records(
        records
    )

    print(
        f"Development records: "
        f"{len(development_records)}"
    )

    print(
        f"Excluded duplicate records: "
        f"{len(excluded_records)}"
    )

    if not development_records:
        raise RuntimeError(
            "No records remain for development."
        )

    (
        train_records,
        validation_records,
    ) = stratified_split(
        development_records
    )

    verify_no_duplicate_leakage(
        train_records,
        validation_records,
    )

    write_split(
        train_records,
        validation_records,
        excluded_records,
    )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    train_distribution = Counter(
        int(record["diagnosis"])
        for record in train_records
    )

    validation_distribution = Counter(
        int(record["diagnosis"])
        for record in validation_records
    )

    print("\nSplit summary:")

    print(
        f"  Train:             "
        f"{len(train_records)}"
    )

    print(
        f"  Validation:        "
        f"{len(validation_records)}"
    )

    print(
        f"  Excluded:          "
        f"{len(excluded_records)}"
    )

    print(
        f"  Total:             "
        f"{len(records)}"
    )

    print("\nTraining distribution:")

    for grade in range(5):
        print(
            f"  Grade {grade}: "
            f"{train_distribution.get(grade, 0)}"
        )

    print("\nValidation distribution:")

    for grade in range(5):
        print(
            f"  Grade {grade}: "
            f"{validation_distribution.get(grade, 0)}"
        )

    print("\nLeakage verification:")
    print(
        "  Train/validation SHA-256 overlap: 0"
    )

    print(
        "\nSplit file written to:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print(
        "\nRaw APTOS dataset was not modified."
    )

    print(
        f"\nRandom seed: {RANDOM_SEED}"
    )

    print(
        f"Validation ratio: "
        f"{VALIDATION_RATIO:.0%}"
    )


if __name__ == "__main__":
    main()