"""EfficientNet-B0 model for ICDR 0-4 classification."""

import torch
from torch import nn
from torchvision.models import (
    EfficientNet_B0_Weights,
    efficientnet_b0,
)


NUM_CLASSES = 5


def build_model(
    num_classes: int = NUM_CLASSES,
    pretrained: bool = True,
    freeze_backbone: bool = True,
) -> nn.Module:
    """Build an EfficientNet-B0 classifier."""

    weights = (
        EfficientNet_B0_Weights.DEFAULT
        if pretrained
        else None
    )

    model = efficientnet_b0(weights=weights)

    if freeze_backbone:
        for parameter in model.features.parameters():
            parameter.requires_grad = False

    classifier_input_features = model.classifier[-1].in_features

    model.classifier[-1] = nn.Linear(
        classifier_input_features,
        num_classes,
    )

    return model


def get_device() -> torch.device:
    """Return CUDA when available, otherwise CPU."""

    return torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )