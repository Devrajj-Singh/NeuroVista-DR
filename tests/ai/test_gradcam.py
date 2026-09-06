"""Tests for the NeuroVista-DR Grad-CAM explainability pipeline."""

import numpy as np
import pytest
import torch

from src.ai.classification.model import build_model
from src.ai.explainability.gradcam import (
    GradCAM,
    create_overlay,
    resize_heatmap,
)


@pytest.fixture
def gradcam_setup():
    """Create a lightweight EfficientNet-B0 Grad-CAM setup."""
    model = build_model(
        pretrained=False,
        freeze_backbone=True,
    )

    device = torch.device("cpu")
    target_layer = model.features[8]

    gradcam = GradCAM(
        model=model,
        target_layer=target_layer,
        device=device,
    )

    return gradcam


def test_gradcam_generates_valid_heatmap(gradcam_setup):
    """Grad-CAM should generate a normalized 2D heatmap."""
    input_tensor = torch.rand(1, 3, 224, 224)

    heatmap, target_class, probabilities = gradcam_setup.generate(
        input_tensor
    )

    assert heatmap.ndim == 2
    assert heatmap.shape[0] > 0
    assert heatmap.shape[1] > 0

    assert np.isfinite(heatmap).all()
    assert heatmap.min() >= 0.0
    assert heatmap.max() <= 1.0

    assert 0 <= target_class <= 4


def test_gradcam_probabilities_are_valid(gradcam_setup):
    """Model probabilities should contain five classes and sum to one."""
    input_tensor = torch.rand(1, 3, 224, 224)

    _, _, probabilities = gradcam_setup.generate(input_tensor)

    assert probabilities.shape == (5,)
    assert np.isfinite(probabilities).all()
    assert np.all(probabilities >= 0.0)
    assert np.all(probabilities <= 1.0)
    assert np.isclose(probabilities.sum(), 1.0, atol=1e-5)


def test_gradcam_specific_target_class(gradcam_setup):
    """Grad-CAM should allow explanation of a specific ICDR class."""
    input_tensor = torch.rand(1, 3, 224, 224)

    for target_class in range(5):
        heatmap, explained_class, probabilities = gradcam_setup.generate(
            input_tensor,
            target_class=target_class,
        )

        assert explained_class == target_class
        assert heatmap.ndim == 2
        assert np.isfinite(heatmap).all()
        assert probabilities.shape == (5,)


def test_gradcam_rejects_invalid_target_class(gradcam_setup):
    """Invalid ICDR classes should raise ValueError."""
    input_tensor = torch.rand(1, 3, 224, 224)

    with pytest.raises(ValueError):
        gradcam_setup.generate(
            input_tensor,
            target_class=5,
        )

    with pytest.raises(ValueError):
        gradcam_setup.generate(
            input_tensor,
            target_class=-1,
        )


def test_resize_heatmap():
    """Heatmap resizing should produce the requested dimensions."""
    heatmap = np.random.rand(7, 7).astype(np.float32)

    resized = resize_heatmap(
        heatmap,
        width=320,
        height=240,
    )

    assert resized.shape == (240, 320)
    assert resized.dtype == np.float32
    assert resized.min() >= 0.0
    assert resized.max() <= 1.0


def test_create_overlay():
    """Grad-CAM overlay should match the original image dimensions."""
    image = np.random.randint(
        0,
        256,
        size=(240, 320, 3),
        dtype=np.uint8,
    )

    heatmap = np.random.rand(7, 7).astype(np.float32)

    overlay = create_overlay(
        image=image,
        heatmap=heatmap,
    )

    assert overlay.shape == image.shape
    assert overlay.dtype == np.uint8
    assert np.isfinite(overlay).all()