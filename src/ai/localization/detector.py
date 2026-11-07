"""Adaptive image-processing baseline for optic disc and fovea localization.

Returns estimated (x, y) pixel centers for a BGR fundus image.
This is an experimental heuristic, not a clinically validated detector.
"""

from typing import Optional

import cv2
import numpy as np


def validate_center(
    center: Optional[tuple[int, int]],
    image_width: int,
    image_height: int,
) -> bool:
    """Return whether a predicted (x, y) center is inside the image."""
    if center is None or image_width <= 0 or image_height <= 0:
        return False

    x, y = center
    return 0 <= x < image_width and 0 <= y < image_height


def localize_centers(
    image: np.ndarray,
) -> dict[str, Optional[tuple[int, int]]]:
    """Estimate optic disc and fovea centers in a BGR fundus image."""
    result: dict[str, Optional[tuple[int, int]]] = {
        "optic_disc": None,
        "fovea": None,
    }

    if (
        not isinstance(image, np.ndarray)
        or image.ndim != 3
        or image.shape[2] != 3
        or image.shape[0] < 20
        or image.shape[1] < 20
    ):
        return result

    height, width = image.shape[:2]
    green = cv2.GaussianBlur(image[:, :, 1], (9, 9), 0)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    retinal_mask = (gray > 10).astype(np.uint8)

    if cv2.countNonZero(retinal_mask) == 0:
        return result

    retinal_values = green[retinal_mask > 0]
    threshold = float(np.percentile(retinal_values, 99.5))
    bright_mask = (green >= threshold).astype(np.uint8) * retinal_mask

    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        bright_mask, connectivity=8
    )

    retinal_area = cv2.countNonZero(retinal_mask)
    candidates = []

    for label in range(1, count):
        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        w = int(stats[label, cv2.CC_STAT_WIDTH])
        h = int(stats[label, cv2.CC_STAT_HEIGHT])
        area = int(stats[label, cv2.CC_STAT_AREA])

        touches_edge = (
            x == 0
            or y == 0
            or x + w >= width
            or y + h >= height
        )

        if (
            not touches_edge
            and 0.0002 * retinal_area <= area <= 0.08 * retinal_area
        ):
            candidates.append((area, centroids[label]))

    if not candidates:
        return result

    area, (disc_x, disc_y) = max(
        candidates, key=lambda item: item[0]
    )

    disc_center = (
        int(round(float(disc_x))),
        int(round(float(disc_y))),
    )

    if not validate_center(disc_center, width, height):
        return result

    result["optic_disc"] = disc_center

    # Search farther from the optic disc for the fovea.
    direction = 1 if disc_x < width / 2 else -1

    start_x = int(disc_x + direction * 900)
    end_x = int(disc_x + direction * 1450)

    x_min = max(0, min(start_x, end_x))
    x_max = min(width, max(start_x, end_x) + 1)
    y_min = max(0, int(disc_y - 450))
    y_max = min(height, int(disc_y + 450) + 1)

    if x_min >= x_max or y_min >= y_max:
        return result

    region = green[y_min:y_max, x_min:x_max]
    region_mask = retinal_mask[y_min:y_max, x_min:x_max] > 0

    if not np.any(region_mask):
        return result

    # Smooth the intensity map to reduce the influence of individual vessels.
    smoothed = cv2.GaussianBlur(region, (51, 51), 0)

    valid_values = smoothed[region_mask]
    darkness_threshold = float(np.percentile(valid_values, 10))

    dark_mask = (
        (smoothed <= darkness_threshold) & region_mask
    ).astype(np.uint8)

    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        dark_mask, connectivity=8
    )

    dark_candidates = []

    for label in range(1, count):
        candidate_area = int(stats[label, cv2.CC_STAT_AREA])

        if candidate_area >= 20:
            dark_candidates.append(
                (candidate_area, centroids[label])
            )

    if not dark_candidates:
        return result

    _, (local_x, local_y) = max(
        dark_candidates, key=lambda item: item[0]
    )

    fovea_center = (
        x_min + int(round(float(local_x))),
        y_min + int(round(float(local_y))),
    )

    if validate_center(fovea_center, width, height):
        result["fovea"] = fovea_center

    return result