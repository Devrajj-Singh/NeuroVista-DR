"""
Generate a duplicate-aware metadata manifest for the APTOS 2019 dataset.

Input:
    data/raw/aptos/aptos2019-blindness-detection/train_images/
    data/raw/aptos/aptos2019-blindness-detection/train.csv

Output:
    data/metadata/aptos_metadata.csv

The raw dataset is never modified.
"""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "aptos"
    / "aptos2019-blindness-detection"
)

IMAGE_DIR = DATASET_ROOT / "train_images"
LABEL_FILE = DATASET_ROOT / "train.csv"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "aptos_metadata.csv"
)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
}


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_labels() -> dict[str, int]:
    """Load APTOS diagnosis labels."""

    if not LABEL_FILE.exists():
        raise FileNotFoundError(
            f"APTOS label file not found: {LABEL_FILE}"
        )

    labels = {}

    with LABEL_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                "APTOS CSV has no header."
            )

        reader.fieldnames = [
            header.strip().lstrip("\ufeff")
            for header in reader.fieldnames
        ]

        required = {
            "id_code",
            "diagnosis",
        }

        missing = required - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

        for row in reader:

            image_id = (
                row["id_code"] or ""
            ).strip()

            diagnosis = (
                row["diagnosis"] or ""
            ).strip()

            if not image_id:
                raise ValueError(
                    "Encountered empty image ID."
                )

            grade = int(diagnosis)

            if grade not in {0, 1, 2, 3, 4}:
                raise ValueError(
                    f"Invalid diagnosis {grade} "
                    f"for image {image_id}"
                )

            if image_id in labels:
                raise ValueError(
                    f"Duplicate label ID: {image_id}"
                )

            labels[image_id] = grade

    return labels


def find_images() -> list[Path]:
    """Find all APTOS training images."""

    if not IMAGE_DIR.exists():
        raise FileNotFoundError(
            f"APTOS image directory not found: {IMAGE_DIR}"
        )

    return sorted(
        path
        for path in IMAGE_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower()
        in SUPPORTED_EXTENSIONS
    )


def main() -> None:
    """Generate APTOS metadata manifest."""

    print("=" * 70)
    print("APTOS Metadata Manifest Generator")
    print("=" * 70)

    labels = load_labels()
    images = find_images()

    print(f"\nImages discovered: {len(images)}")
    print(f"Labels loaded:     {len(labels)}")

    image_records = []

    for image_path in images:

        image_id = image_path.stem

        image_records.append(
            {
                "image_id": image_id,
                "filename": image_path.name,
                "relative_path": str(
                    image_path.relative_to(PROJECT_ROOT)
                ),
                "sha256": calculate_sha256(
                    image_path
                ),
                "diagnosis": labels.get(
                    image_id
                ),
            }
        )

    # ---------------------------------------------------------------
    # Validate image ↔ label mapping
    # ---------------------------------------------------------------

    image_ids = {
        record["image_id"]
        for record in image_records
    }

    missing_labels = sorted(
        image_ids - set(labels)
    )

    orphan_labels = sorted(
        set(labels) - image_ids
    )

    if missing_labels:
        raise RuntimeError(
            "Images without labels detected: "
            + ", ".join(missing_labels)
        )

    if orphan_labels:
        raise RuntimeError(
            "Labels without images detected: "
            + ", ".join(orphan_labels)
        )

    # ---------------------------------------------------------------
    # Group exact duplicate image contents
    # ---------------------------------------------------------------

    hash_groups = defaultdict(list)

    for record in image_records:
        hash_groups[
            record["sha256"]
        ].append(record)

    duplicate_groups = {
        image_hash: records
        for image_hash, records
        in hash_groups.items()
        if len(records) > 1
    }

    print(
        f"Duplicate groups:  "
        f"{len(duplicate_groups)}"
    )

    # ---------------------------------------------------------------
    # Assign deterministic duplicate IDs
    # ---------------------------------------------------------------

    sorted_duplicate_hashes = sorted(
        duplicate_groups
    )

    duplicate_id_by_hash = {}

    for index, image_hash in enumerate(
        sorted_duplicate_hashes,
        start=1,
    ):
        duplicate_id_by_hash[
            image_hash
        ] = f"DUP-{index:03d}"

    # ---------------------------------------------------------------
    # Build final records
    # ---------------------------------------------------------------

    for record in image_records:

        image_hash = record["sha256"]

        if image_hash in duplicate_id_by_hash:

            duplicate_id = (
                duplicate_id_by_hash[
                    image_hash
                ]
            )

            group = duplicate_groups[
                image_hash
            ]

            grades = {
                item["diagnosis"]
                for item in group
            }

            record["duplicate_group"] = (
                duplicate_id
            )

            record["is_duplicate"] = "yes"

            if len(grades) > 1:
                record["duplicate_status"] = (
                    "conflicting_label"
                )
            else:
                record["duplicate_status"] = (
                    "exact_duplicate"
                )

        else:

            record["duplicate_group"] = ""

            record["is_duplicate"] = "no"

            record["duplicate_status"] = (
                "unique"
            )

        record["dataset_split"] = (
            "training_source"
        )

    # ---------------------------------------------------------------
    # Write manifest
    # ---------------------------------------------------------------

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
        "dataset_split",
        "duplicate_group",
        "is_duplicate",
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

        for record in sorted(
            image_records,
            key=lambda item: item["image_id"],
        ):
            writer.writerow(record)

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    unique_records = sum(
        1
        for record in image_records
        if record["is_duplicate"] == "no"
    )

    duplicate_records = len(
        image_records
    ) - unique_records

    conflicting_groups = sum(
        1
        for records
        in duplicate_groups.values()
        if len(
            {
                record["diagnosis"]
                for record in records
            }
        ) > 1
    )

    print("\nManifest summary:")
    print(
        f"  Total image records: "
        f"{len(image_records)}"
    )

    print(
        f"  Unique image records: "
        f"{unique_records}"
    )

    print(
        f"  Duplicate records: "
        f"{duplicate_records}"
    )

    print(
        f"  Duplicate groups: "
        f"{len(duplicate_groups)}"
    )

    print(
        f"  Conflicting-label groups: "
        f"{conflicting_groups}"
    )

    print(
        f"\nManifest written to:\n"
        f"{OUTPUT_FILE}"
    )

    print("\nRaw dataset was not modified.")


if __name__ == "__main__":
    main()