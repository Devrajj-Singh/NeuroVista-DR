"""Image-quality gate for the NeuroVista-DR pipeline.

Accepts or rejects a fundus image based on lightweight, explainable
image-statistics checks (blur and darkness). This runs *before* the DR
classifier so that a rejected image never reaches classification.

Notes:
    This is a heuristic quality gate using standard image-processing
    metrics. It is intentionally deterministic and free of external
    CV/ML dependencies so that it can run in minimal environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from PIL import Image, ImageStat

QualityStatus = Literal["good", "ungradable"]
QualityReason = Literal[
    "low_focus",
    "too_dark",
    "poor_field_of_view",
    "insufficient_quality",
]


@dataclass(frozen=True)
class QualityConfig:
    """Tunable thresholds for the quality gate."""

    # Blur: normalized interior Laplacian variance (higher = sharper).
    # Normalizing by the interior mean/std removes dependence on exposure
    # and image size, so a bright-but-blurred image is still rejected.
    min_interior_laplacian_var: float = 5.0

    # Darkness: mean grayscale in [0, 255].
    min_mean_luminance: float = 24.0
    max_mean_luminance: float = 235.0

    # Field of view: fraction of bright pixels near the image center.
    min_field_fraction: float = 0.06


DEFAULT_CONFIG = QualityConfig()


@dataclass(frozen=True)
class QualityResult:
    """Outcome of the quality gate."""

    status: QualityStatus
    reason: QualityReason | None = None
    # Diagnostics (debugging/telemetry only, not part of the UI contract).
    metrics: dict[str, float] | None = None


def _interior_laplacian_variance(image: Image.Image) -> float:
    """Estimate sharpness from the normalized interior Laplacian variance.

    The interior crop excludes the large optic-disc boundary so that a
    bright-but-blurred image is not spuriously judged sharp. The grayscale
    interior is standardized (zero-mean, unit variance) before applying the
    Laplacian kernel, which makes the metric independent of exposure and
    image size.
    """
    grayscale = image.convert("L").resize((224, 224))
    interior = grayscale.crop((70, 70, 154, 154))

    pixels = np.asarray(interior, dtype=np.float32)
    std = float(pixels.std())
    if std < 1e-6:
        # A perfectly flat interior has no edge structure at all.
        return 0.0
    pixels = (pixels - pixels.mean()) / std

    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    windows = np.lib.stride_tricks.sliding_window_view(pixels, (3, 3))
    laplacian = np.tensordot(windows, kernel, axes=([2, 3], [0, 1]))

    return float(laplacian.var())


def _mean_luminance(image: Image.Image) -> float:
    """Mean luminance of the image in [0, 255]."""
    grayscale = image.convert("L")
    stat = ImageStat.Stat(grayscale)
    return float(stat.mean[0])


def _field_fraction(image: Image.Image) -> float:
    """Fraction of the central region that is bright (retinal disc)."""
    grayscale = image.convert("L")
    width, height = grayscale.size

    # Central crop: the optic disc/retina should occupy the centre.
    crop_box = (
        int(width * 0.30),
        int(height * 0.30),
        int(width * 0.70),
        int(height * 0.70),
    )
    central = grayscale.crop(crop_box)
    pixels = np.asarray(central, dtype=np.uint8)

    # A usable field of view has a meaningful share of mid/bright pixels.
    bright = float(np.mean(pixels > 28))
    return bright


def assess_quality(
    image: Image.Image,
    config: QualityConfig = DEFAULT_CONFIG,
) -> QualityResult:
    """Evaluate an image and return the quality verdict.

    A rejected image returns ``status="ungradable"`` with a reason and the
    pipeline **must not** continue to DR classification.
    """
    metrics = {
        "interior_laplacian_var": _interior_laplacian_variance(image),
        "mean_luminance": _mean_luminance(image),
        "field_fraction": _field_fraction(image),
    }

    # Check exposure first so that a very dark, flat image is reported as
    # "too_dark" rather than a more ambiguous "low_focus".
    if (
        metrics["mean_luminance"] < config.min_mean_luminance
        or metrics["mean_luminance"] > config.max_mean_luminance
    ):
        return QualityResult(status="ungradable", reason="too_dark", metrics=metrics)

    if metrics["field_fraction"] < config.min_field_fraction:
        return QualityResult(status="ungradable", reason="poor_field_of_view", metrics=metrics)

    if metrics["interior_laplacian_var"] < config.min_interior_laplacian_var:
        return QualityResult(status="ungradable", reason="low_focus", metrics=metrics)

    return QualityResult(status="good", reason=None, metrics=metrics)
