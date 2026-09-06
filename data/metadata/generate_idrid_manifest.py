from pathlib import Path
import csv
import hashlib


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IDRID_ROOT = PROJECT_ROOT / "data" / "raw" / "IDRiD" / "B. Disease Grading"
TRAIN_DIR = IDRID_ROOT / "1. Original Images" / "a. Training Set"
TEST_DIR = IDRID_ROOT / "1. Original Images" / "b. Testing Set"

TRAIN_LABELS = (
    IDRID_ROOT
    / "2. Groundtruths"
    / "a. IDRiD_Disease Grading_Training Labels.csv"
)

TEST_LABELS = (
    IDRID_ROOT
    / "2. Groundtruths"
    / "b. IDRiD_Disease Grading_Testing Labels.csv"
)

OUTPUT = PROJECT_ROOT / "data" / "metadata" / "idrid_manifest.csv"


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def load_labels(csv_path: Path, split: str) -> dict:
    labels = {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError(f"No CSV header found: {csv_path}")

        # Normalize headers
        reader.fieldnames = [
            field.strip() if field else field
            for field in reader.fieldnames
        ]

        required = {
            "Image name",
            "Retinopathy grade",
            "Risk of macular edema",
        }

        missing = required - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Missing columns in {csv_path}: {sorted(missing)}"
            )

        for row in reader:
            image_id = row["Image name"].strip()

            labels[(split, image_id)] = {
                "retinopathy_grade": row["Retinopathy grade"].strip(),
                "macular_edema_grade": row["Risk of macular edema"].strip(),
            }

    return labels


def image_dimensions_and_channels(path: Path):
    try:
        from PIL import Image

        with Image.open(path) as img:
            width, height = img.size
            channels = len(img.getbands())

        return width, height, channels

    except Exception:
        return "", "", ""


def discover_images(directory: Path, split: str):
    records = []

    for path in sorted(directory.glob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        image_id = path.stem

        records.append(
            {
                "image_id": image_id,
                "split": split,
                "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "_absolute_path": path,
            }
        )

    return records


def main():
    print("Generating IDRiD manifest...")
    print()

    train_labels = load_labels(TRAIN_LABELS, "training")
    test_labels = load_labels(TEST_LABELS, "testing")

    labels = {}
    labels.update(train_labels)
    labels.update(test_labels)

    records = []

    records.extend(discover_images(TRAIN_DIR, "training"))
    records.extend(discover_images(TEST_DIR, "testing"))

    print(f"Images discovered: {len(records)}")

    # ------------------------------------------------------------
    # Calculate file metadata and SHA-256 hashes
    # ------------------------------------------------------------

    for record in records:
        path = record["_absolute_path"]

        record["sha256"] = sha256_file(path)

        width, height, channels = image_dimensions_and_channels(path)

        record["width"] = width
        record["height"] = height
        record["channels"] = channels

        label_key = (record["split"], record["image_id"])

        label = labels.get(label_key)

        if label:
            record["retinopathy_grade"] = label["retinopathy_grade"]
            record["macular_edema_grade"] = label["macular_edema_grade"]
        else:
            record["retinopathy_grade"] = ""
            record["macular_edema_grade"] = ""

    # ------------------------------------------------------------
    # Group records by SHA-256
    # ------------------------------------------------------------

    hash_groups = {}

    for record in records:
        hash_groups.setdefault(record["sha256"], []).append(record)

    duplicate_groups = {
        file_hash: group
        for file_hash, group in hash_groups.items()
        if len(group) > 1
    }

    print(f"Duplicate groups: {len(duplicate_groups)}")

    # ------------------------------------------------------------
    # Assign stable duplicate group IDs
    # ------------------------------------------------------------

    sorted_duplicate_hashes = sorted(duplicate_groups.keys())

    hash_to_duplicate_id = {
        file_hash: f"DUP-{index:03d}"
        for index, file_hash in enumerate(
            sorted_duplicate_hashes,
            start=1,
        )
    }

    # ------------------------------------------------------------
    # Analyse duplicate groups
    # ------------------------------------------------------------

    for file_hash, group in duplicate_groups.items():

        duplicate_id = hash_to_duplicate_id[file_hash]

        splits = {record["split"] for record in group}

        cross_split = len(splits) > 1

        labels_in_group = {
            (
                record["retinopathy_grade"],
                record["macular_edema_grade"],
            )
            for record in group
        }

        conflicting_labels = len(labels_in_group) > 1

        for record in group:
            record["duplicate_group"] = duplicate_id
            record["cross_split_duplicate"] = (
                "yes" if cross_split else "no"
            )
            record["conflicting_duplicate_label"] = (
                "yes" if conflicting_labels else "no"
            )

            if cross_split:
                record["validation_status"] = (
                    "exclude_from_evaluation"
                )

            elif conflicting_labels:
                record["validation_status"] = (
                    "review_duplicate_label"
                )

            else:
                record["validation_status"] = "valid"

    # ------------------------------------------------------------
    # Mark non-duplicate records
    # ------------------------------------------------------------

    for record in records:
        if "duplicate_group" not in record:
            record["duplicate_group"] = ""
            record["cross_split_duplicate"] = "no"
            record["conflicting_duplicate_label"] = "no"

            if (
                record["retinopathy_grade"] == ""
                or record["macular_edema_grade"] == ""
            ):
                record["validation_status"] = "missing_label"
            else:
                record["validation_status"] = "valid"

    # ------------------------------------------------------------
    # Write manifest
    # ------------------------------------------------------------

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "image_id",
        "split",
        "path",
        "sha256",
        "width",
        "height",
        "channels",
        "retinopathy_grade",
        "macular_edema_grade",
        "duplicate_group",
        "cross_split_duplicate",
        "conflicting_duplicate_label",
        "validation_status",
    ]

    with OUTPUT.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in sorted(
            records,
            key=lambda r: (
                r["split"],
                r["image_id"],
            ),
        ):

            writer.writerow(
                {
                    field: record[field]
                    for field in fieldnames
                }
            )

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    status_counts = {}

    for record in records:
        status = record["validation_status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    cross_split_groups = sum(
        1
        for group in duplicate_groups.values()
        if len({record["split"] for record in group}) > 1
    )

    conflicting_groups = sum(
        1
        for group in duplicate_groups.values()
        if len(
            {
                (
                    record["retinopathy_grade"],
                    record["macular_edema_grade"],
                )
                for record in group
            }
        )
        > 1
    )

    print()
    print("Manifest written:")
    print(OUTPUT)
    print()

    print("Validation status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print()
    print(f"Cross-split duplicate groups: {cross_split_groups}")
    print(f"Conflicting-label duplicate groups: {conflicting_groups}")


if __name__ == "__main__":
    main()