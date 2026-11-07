"""Evaluate optic disc and fovea localization against IDRiD annotations."""

import math
import statistics
from pathlib import Path

import cv2

from src.ai.localization.annotations import load_center_annotations
from src.ai.localization.detector import localize_centers


ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "data" / "raw" / "IDRiD" / "a. Training Set"
ANNOTATION_DIR = ROOT / "data" / "localization"

ANNOTATIONS = {
    "optic_disc": (
        ANNOTATION_DIR / "a. IDRiD_OD_Center_Training Set_Markups.csv"
    ),
    "fovea": (
        ANNOTATION_DIR / "IDRiD_Fovea_Center_Training Set_Markups.csv"
    ),
}


def main() -> None:
    """Evaluate predictions for images with both annotations."""
    annotations = {
        name: load_center_annotations(path)
        for name, path in ANNOTATIONS.items()
    }

    image_ids = sorted(
        set(annotations["optic_disc"]) & set(annotations["fovea"])
    )

    errors = {"optic_disc": [], "fovea": []}
    missing = {"optic_disc": 0, "fovea": 0}
    unreadable = 0

    for image_id in image_ids:
        image_path = IMAGE_DIR / f"{image_id}.jpg"
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"Warning: Could not read {image_path}")
            unreadable += 1
            continue

        predictions = localize_centers(image)

        for name in ("optic_disc", "fovea"):
            predicted = predictions[name]

            if predicted is None:
                missing[name] += 1
                continue

            actual = annotations[name][image_id]
            errors[name].append(math.dist(actual, predicted))

    print("\nIDRiD TRAINING SET EVALUATION")
    print(f"Images with both annotations: {len(image_ids)}")
    print(f"Unreadable images: {unreadable}")

    for name in ("optic_disc", "fovea"):
        distances = errors[name]
        print(f"\n{name.replace('_', ' ').title()}:")

        if distances:
            print(f"  Evaluated images: {len(distances)}")
            print(f"  Mean error: {statistics.mean(distances):.2f} pixels")
            print(f"  Median error: {statistics.median(distances):.2f} pixels")
        else:
            print("  No successful predictions.")

        print(f"  Missing predictions: {missing[name]}")


if __name__ == "__main__":
    main()