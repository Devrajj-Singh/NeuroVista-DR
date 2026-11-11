from pathlib import Path
import csv
import hashlib
from collections import Counter

from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_PATH = PROJECT_ROOT / "data" / "metadata" / "idrid_manifest.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "metadata" / "idrid_project_split.csv"


def get_file_hash(file_path):
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    with open(MANIFEST_PATH, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        manifest = list(reader)

    required_columns = {
        "image_id",
        "path",
        "retinopathy_grade",
        "split"
    }

    if not manifest or not required_columns.issubset(manifest[0].keys()):
        raise ValueError("Manifest is missing required columns.")

    official_training = [
        row for row in manifest
        if row["split"].strip().lower() in ("training", "train")
    ]

    official_testing = len(manifest) - len(official_training)

    print("Official training records:", len(official_training))
    print("Official testing records excluded:", official_testing)

    unique_records = []
    seen_hashes = set()

    for row in official_training:
        image_path = Path(row["path"])

        if not image_path.is_absolute():
            image_path = PROJECT_ROOT / image_path

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image_hash = get_file_hash(image_path)

        if image_hash not in seen_hashes:
            seen_hashes.add(image_hash)

            updated_row = row.copy()
            updated_row["path"] = image_path.relative_to(PROJECT_ROOT).as_posix()
            unique_records.append(updated_row)

    print("Duplicate images excluded:",
          len(official_training) - len(unique_records))
    print("Unique training images:", len(unique_records))

    grades = [
        row["retinopathy_grade"]
        for row in unique_records
    ]

    train_records, validation_records = train_test_split(
        unique_records,
        test_size=0.20,
        random_state=42,
        stratify=grades
    )

    output_records = []

    for row in train_records:
        output_records.append({
            "image_id": row["image_id"],
            "path": row["path"],
            "retinopathy_grade": row["retinopathy_grade"],
            "project_split": "train"
        })

    for row in validation_records:
        output_records.append({
            "image_id": row["image_id"],
            "path": row["path"],
            "retinopathy_grade": row["retinopathy_grade"],
            "project_split": "validation"
        })

    fieldnames = [
        "image_id",
        "path",
        "retinopathy_grade",
        "project_split"
    ]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_records)

    split_counts = Counter(
        row["project_split"] for row in output_records
    )

    print("\nFinal split counts:")
    print("Train:", split_counts["train"])
    print("Validation:", split_counts["validation"])

    train_ids = {
        row["image_id"] for row in output_records
        if row["project_split"] == "train"
    }

    validation_ids = {
        row["image_id"] for row in output_records
        if row["project_split"] == "validation"
    }

    if train_ids.intersection(validation_ids):
        raise ValueError("Train-validation leakage detected!")

    print("No train-validation leakage detected.")
    print("\nOutput saved to:", OUTPUT_PATH)
    print("IDRiD SPLIT GENERATION COMPLETE")


if __name__ == "__main__":
    main()