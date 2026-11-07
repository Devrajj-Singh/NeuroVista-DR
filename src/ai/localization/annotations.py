
"""Load IDRiD optic disc and fovea center annotations."""

import csv
from pathlib import Path


def load_center_annotations(
    csv_path: str | Path,
) -> dict[str, tuple[int, int]]:
    """Load image IDs and their annotated (x, y) center coordinates."""
    path = Path(csv_path)

    if not path.is_file():
        raise FileNotFoundError(f"Annotation CSV not found: {path}")

    result: dict[str, tuple[int, int]] = {}

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "Image No",
            "X- Coordinate",
            "Y - Coordinate",
        }

        if reader.fieldnames is None:
            raise ValueError("Annotation CSV has no header row.")

        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Annotation CSV is missing required columns: {sorted(missing)}"
            )

        for row in reader:
            image_id = (row.get("Image No") or "").strip()

            # Skip completely empty rows in the CSV.
            if not any((value or "").strip() for value in row.values()):
                continue

            if not image_id:
                raise ValueError(
                    "Annotation CSV contains a missing image ID."
                )

            if image_id in result:
                raise ValueError(
                    f"Duplicate annotation for image {image_id}."
                )

            try:
                x = float(row["X- Coordinate"])
                y = float(row["Y - Coordinate"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid coordinates for image {image_id}."
                ) from None

            if not (x >= 0 and y >= 0):
                raise ValueError(
                    "Annotation coordinates cannot be negative."
                )

            if not (x.is_integer() and y.is_integer()):
                raise ValueError(
                    f"Coordinates must be integers for image {image_id}."
                )

            result[image_id] = (int(x), int(y))

    return result
