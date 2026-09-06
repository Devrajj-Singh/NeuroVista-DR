from pathlib import Path
import csv
import random
from collections import Counter, defaultdict


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MANIFEST = PROJECT_ROOT / "data" / "metadata" / "idrid_manifest.csv"
OUTPUT = PROJECT_ROOT / "data" / "metadata" / "idrid_project_split.csv"

SEED = 42
TRAIN_RATIO = 0.80


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    records = load_manifest()

    print(f"Manifest records: {len(records)}")

    # ------------------------------------------------------------
    # 1. Identify every duplicate SHA-256 group.
    #
    #    Any duplicate image is excluded from the clean project
    #    split, even when its labels agree.
    #
    #    This prevents duplicate-image leakage between train and
    #    validation and avoids relying on duplicated observations.
    # ------------------------------------------------------------

    hash_groups = defaultdict(list)

    for record in records:
        hash_groups[record["sha256"]].append(record)

    duplicate_groups = {
        file_hash: group
        for file_hash, group in hash_groups.items()
        if len(group) > 1
    }

    duplicate_records = {
        id(record): record
        for group in duplicate_groups.values()
        for record in group
    }

    print(f"Duplicate groups: {len(duplicate_groups)}")
    print(
        f"Records belonging to duplicate groups: "
        f"{len(duplicate_records)}"
    )

    # ------------------------------------------------------------
    # 2. Build clean candidate set.
    # ------------------------------------------------------------

    candidates = []
    excluded = []

    for record in records:

        if id(record) in duplicate_records:
            record["project_split"] = "excluded"

            if record["cross_split_duplicate"] == "yes":
                record["exclusion_reason"] = (
                    "duplicate_image_cross_split"
                )
            elif record["conflicting_duplicate_label"] == "yes":
                record["exclusion_reason"] = (
                    "duplicate_image_conflicting_label"
                )
            else:
                record["exclusion_reason"] = (
                    "duplicate_image"
                )

            excluded.append(record)

        else:
            candidates.append(record)

    print(f"Clean candidate records: {len(candidates)}")
    print(f"Excluded records: {len(excluded)}")

    # ------------------------------------------------------------
    # 3. Verify that every candidate SHA-256 is unique.
    # ------------------------------------------------------------

    candidate_hashes = [
        record["sha256"]
        for record in candidates
    ]

    if len(candidate_hashes) != len(set(candidate_hashes)):
        raise RuntimeError(
            "Duplicate SHA-256 hashes remain in the candidate set."
        )

    print("Candidate uniqueness check: PASS")

    # ------------------------------------------------------------
    # 4. Validate DR labels.
    # ------------------------------------------------------------

    for record in candidates:
        if record["retinopathy_grade"] == "":
            raise RuntimeError(
                f"Missing DR grade for {record['image_id']}"
            )

    # ------------------------------------------------------------
    # 5. Stratified train/validation split by DR grade.
    # ------------------------------------------------------------

    grade_groups = defaultdict(list)

    for record in candidates:
        grade_groups[
            record["retinopathy_grade"]
        ].append(record)

    rng = random.Random(SEED)

    train_records = []
    validation_records = []

    for grade in sorted(grade_groups):

        group = grade_groups[grade]

        rng.shuffle(group)

        if len(group) == 1:
            train_count = 1
        else:
            train_count = round(
                len(group) * TRAIN_RATIO
            )

            train_count = max(
                1,
                min(
                    train_count,
                    len(group) - 1,
                ),
            )

        train_records.extend(
            group[:train_count]
        )

        validation_records.extend(
            group[train_count:]
        )

    # ------------------------------------------------------------
    # 6. Assign split names.
    # ------------------------------------------------------------

    train_paths = {
        record["path"]
        for record in train_records
    }

    validation_paths = {
        record["path"]
        for record in validation_records
    }

    output_records = []

    for record in records:

        output = dict(record)

        # Remove internal fields if present.
        output.pop("_absolute_path", None)
        output.pop("project_status", None)

        if record["path"] in train_paths:
            output["project_split"] = "train"
            output["exclusion_reason"] = ""

        elif record["path"] in validation_paths:
            output["project_split"] = "validation"
            output["exclusion_reason"] = ""

        else:
            output["project_split"] = "excluded"

            if record["cross_split_duplicate"] == "yes":
                output["exclusion_reason"] = (
                    "duplicate_image_cross_split"
                )
            elif record["conflicting_duplicate_label"] == "yes":
                output["exclusion_reason"] = (
                    "duplicate_image_conflicting_label"
                )
            else:
                output["exclusion_reason"] = (
                    "duplicate_image"
                )

        output_records.append(output)

    # ------------------------------------------------------------
    # 7. Final leakage check.
    # ------------------------------------------------------------

    split_hashes = defaultdict(set)

    for record in output_records:

        split = record["project_split"]

        if split in {"train", "validation"}:
            split_hashes[split].add(
                record["sha256"]
            )

    leakage = (
        split_hashes["train"]
        & split_hashes["validation"]
    )

    if leakage:
        raise RuntimeError(
            "DATA LEAKAGE DETECTED: "
            "identical SHA-256 hashes exist in both "
            "train and validation."
        )

    print("Train/validation SHA-256 leakage check: PASS")

    # ------------------------------------------------------------
    # 8. Write project split manifest.
    # ------------------------------------------------------------

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
        "project_split",
        "exclusion_reason",
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
            output_records,
            key=lambda r: (
                r["project_split"],
                r["retinopathy_grade"],
                r["image_id"],
            ),
        ):

            writer.writerow(
                {
                    field: record.get(field, "")
                    for field in fieldnames
                }
            )

    # ------------------------------------------------------------
    # 9. Summary.
    # ------------------------------------------------------------

    print()
    print("Project split generated:")
    print(OUTPUT)

    print()
    print("Split counts:")
    print(
        f"  Train:       {len(train_records)}"
    )
    print(
        f"  Validation:  {len(validation_records)}"
    )
    print(
        f"  Excluded:    {len(excluded)}"
    )
    print(
        f"  Total:       {len(output_records)}"
    )

    print()
    print("Training DR distribution:")

    train_distribution = Counter(
        record["retinopathy_grade"]
        for record in train_records
    )

    for grade in sorted(train_distribution):
        print(
            f"  Grade {grade}: "
            f"{train_distribution[grade]}"
        )

    print()
    print("Validation DR distribution:")

    validation_distribution = Counter(
        record["retinopathy_grade"]
        for record in validation_records
    )

    for grade in sorted(validation_distribution):
        print(
            f"  Grade {grade}: "
            f"{validation_distribution[grade]}"
        )

    print()
    print(f"Random seed: {SEED}")
    print("Status: SUCCESS")


if __name__ == "__main__":
    main()