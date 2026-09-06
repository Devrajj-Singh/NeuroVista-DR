"""Tests for the NeuroVista-DR baseline classifier."""

import torch

from src.ai.classification.config import NUM_CLASSES
from src.ai.classification.evaluate import (
    calculate_classification_metrics,
    calculate_referable_dr_metrics,
)
from src.ai.classification.model import build_model


def test_model_output_shape():
    """EfficientNet-B0 should output five ICDR classes."""

    model = build_model(
        pretrained=False,
        freeze_backbone=True,
    )

    model.eval()

    sample = torch.randn(1, 3, 224, 224)

    with torch.no_grad():
        output = model(sample)

    assert output.shape == (1, NUM_CLASSES)


def test_classification_metrics():
    """Classification metrics should be calculated correctly."""

    y_true = [0, 1, 2, 3, 4]
    y_pred = [0, 1, 2, 2, 4]

    metrics = calculate_classification_metrics(
        y_true,
        y_pred,
    )

    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["macro_f1"] <= 1.0

    assert len(
        metrics["confusion_matrix"]
    ) == NUM_CLASSES


def test_referable_dr_metrics():
    """Referable DR should use ICDR >= 2."""

    y_true = [0, 1, 2, 3, 4]
    y_pred = [0, 1, 2, 2, 4]

    metrics = calculate_referable_dr_metrics(
        y_true,
        y_pred,
        threshold=2,
    )

    assert metrics["threshold"] == 2

    assert (
        metrics["true_positive"]
        + metrics["false_negative"]
        == 3
    )

    assert (
        metrics["true_negative"]
        + metrics["false_positive"]
        == 2
    )

    assert 0.0 <= metrics["sensitivity"] <= 1.0
    assert 0.0 <= metrics["specificity"] <= 1.0