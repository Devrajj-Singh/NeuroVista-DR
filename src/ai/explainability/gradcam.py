"""Grad-CAM explainability for the NeuroVista-DR classification model.

This module generates Grad-CAM heatmaps for the EfficientNet-B0 ICDR
classification model.

Important:
    Grad-CAM highlights image regions that influence a model prediction.
    It does NOT constitute lesion detection or clinical evidence by itself.
    Lesion-level evidence will be implemented separately using lesion
    segmentation/ground-truth annotations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

from src.ai.classification.config import (
    CLASS_NAMES,
    IMAGE_SIZE,
)
from src.ai.classification.model import build_model, get_device
from src.ai.classification.preprocessing import get_validation_transform


@dataclass
class GradCAMResult:
    """Container for a Grad-CAM prediction and heatmap."""

    predicted_class: int
    class_name: str
    confidence: float
    probabilities: np.ndarray
    heatmap: np.ndarray
    overlay: np.ndarray


class GradCAM:
    """Grad-CAM implementation for a PyTorch classification model."""

    def __init__(
        self,
        model: torch.nn.Module,
        target_layer: torch.nn.Module,
        device: torch.device | None = None,
    ) -> None:
        self.model = model
        self.target_layer = target_layer
        self.device = device or get_device()

        self.activations: torch.Tensor | None = None
        self.gradients: torch.Tensor | None = None

        self._forward_handle = target_layer.register_forward_hook(
            self._forward_hook
        )
        self._backward_handle = target_layer.register_full_backward_hook(
            self._backward_hook
        )

        self.model.to(self.device)
        self.model.eval()

    def _forward_hook(
        self,
        module: torch.nn.Module,
        inputs: tuple[torch.Tensor, ...],
        output: torch.Tensor,
    ) -> None:
        """Store feature maps produced by the target layer."""
        self.activations = output.detach()

    def _backward_hook(
        self,
        module: torch.nn.Module,
        grad_input: tuple[torch.Tensor | None, ...],
        grad_output: tuple[torch.Tensor | None, ...],
    ) -> None:
        """Store gradients flowing through the target layer."""
        if grad_output and grad_output[0] is not None:
            self.gradients = grad_output[0].detach()

    def generate(
        self,
        input_tensor: torch.Tensor,
        target_class: int | None = None,
    ) -> tuple[np.ndarray, int, np.ndarray]:
        """Generate a Grad-CAM heatmap.

        Args:
            input_tensor:
                Preprocessed image tensor with shape [1, 3, H, W].
            target_class:
                Class to explain. If None, explains the predicted class.

        Returns:
            Tuple containing:
                - heatmap as a float32 NumPy array in [0, 1]
                - target class index
                - class probabilities
        """
        input_tensor = input_tensor.to(self.device)
        input_tensor = input_tensor.requires_grad_(True)

        self.model.zero_grad(set_to_none=True)
        self.activations = None
        self.gradients = None

        logits = self.model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)

        predicted_class = int(torch.argmax(probabilities, dim=1).item())

        if target_class is None:
            target_class = predicted_class

        if not 0 <= target_class < logits.shape[1]:
            raise ValueError(
                f"target_class must be between 0 and {logits.shape[1] - 1}"
            )

        score = logits[:, target_class].sum()
        score.backward()

        if self.activations is None:
            raise RuntimeError("Grad-CAM activations were not captured.")

        if self.gradients is None:
            raise RuntimeError("Grad-CAM gradients were not captured.")

        activations = self.activations
        gradients = self.gradients

        # Global average pooling over spatial dimensions.
        weights = gradients.mean(dim=(2, 3), keepdim=True)

        # Weighted combination of feature maps.
        cam = (weights * activations).sum(dim=1, keepdim=True)

        # Keep only positive influence.
        cam = torch.relu(cam)

        # Normalize safely.
        cam_min = cam.min()
        cam_max = cam.max()

        if (cam_max - cam_min).abs() > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = torch.zeros_like(cam)

        heatmap = cam.squeeze().cpu().numpy().astype(np.float32)

        return heatmap, target_class, probabilities.squeeze(0).detach().cpu().numpy()


def load_gradcam_model(
    checkpoint_path: str | Path,
    device: torch.device | None = None,
) -> tuple[torch.nn.Module, GradCAM, torch.device]:
    """Load the NeuroVista-DR classifier and configure Grad-CAM.

    The target layer is EfficientNet-B0's final convolutional feature stage:
    model.features[8].
    """
    device = device or get_device()

    model = build_model(
        pretrained=False,
        freeze_backbone=False,
    )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=True,
    )

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint

    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    # Final convolutional feature stage before global pooling/classifier.
    target_layer = model.features[8]

    gradcam = GradCAM(
        model=model,
        target_layer=target_layer,
        device=device,
    )

    return model, gradcam, device


def load_and_preprocess_image(
    image_path: str | Path,
) -> tuple[torch.Tensor, Image.Image]:
    """Load an image and apply the classifier's validation preprocessing."""
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")

    transform = get_validation_transform(IMAGE_SIZE)
    tensor = transform(image).unsqueeze(0)

    return tensor, image


def resize_heatmap(
    heatmap: np.ndarray,
    width: int,
    height: int,
) -> np.ndarray:
    """Resize a normalized Grad-CAM heatmap to image dimensions."""
    resized = cv2.resize(
        heatmap,
        (width, height),
        interpolation=cv2.INTER_LINEAR,
    )

    return np.clip(resized, 0.0, 1.0).astype(np.float32)


def create_overlay(
    image: Image.Image | np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.4,
) -> np.ndarray:
    """Create a visual Grad-CAM overlay.

    Args:
        image:
            Original RGB image.
        heatmap:
            Normalized Grad-CAM heatmap in [0, 1].
        alpha:
            Heatmap transparency.

    Returns:
        RGB uint8 NumPy image.
    """
    if isinstance(image, Image.Image):
        image_array = np.asarray(image.convert("RGB"))
    else:
        image_array = np.asarray(image)

    if image_array.ndim != 3 or image_array.shape[2] != 3:
        raise ValueError("Expected an RGB image with shape [H, W, 3].")

    height, width = image_array.shape[:2]

    heatmap_resized = resize_heatmap(
        heatmap,
        width=width,
        height=height,
    )

    heatmap_uint8 = np.uint8(255 * heatmap_resized)

    # OpenCV generates the visualization in BGR.
    colored_heatmap = cv2.applyColorMap(
        heatmap_uint8,
        cv2.COLORMAP_JET,
    )

    colored_heatmap = cv2.cvtColor(
        colored_heatmap,
        cv2.COLOR_BGR2RGB,
    )

    image_array = image_array.astype(np.uint8)

    overlay = cv2.addWeighted(
        image_array,
        1.0 - alpha,
        colored_heatmap,
        alpha,
        0,
    )

    return overlay


def explain_image(
    image_path: str | Path,
    checkpoint_path: str | Path,
    target_class: int | None = None,
    alpha: float = 0.4,
) -> GradCAMResult:
    """Run classification and Grad-CAM explanation on one image."""
    _, gradcam, device = load_gradcam_model(
        checkpoint_path=checkpoint_path,
    )

    input_tensor, original_image = load_and_preprocess_image(
        image_path,
    )

    heatmap, explained_class, probabilities = gradcam.generate(
        input_tensor=input_tensor,
        target_class=target_class,
    )

    predicted_class = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_class])

    overlay = create_overlay(
        image=original_image,
        heatmap=heatmap,
        alpha=alpha,
    )

    return GradCAMResult(
        predicted_class=predicted_class,
        class_name=CLASS_NAMES[predicted_class],
        confidence=confidence,
        probabilities=probabilities,
        heatmap=heatmap,
        overlay=overlay,
    )


def save_explanation(
    result: GradCAMResult,
    output_path: str | Path,
) -> None:
    """Save the Grad-CAM overlay as an RGB PNG/JPEG image."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.fromarray(result.overlay)
    image.save(output_path)


def main() -> None:
    """Command-line interface for Grad-CAM inference."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Grad-CAM explanation for a NeuroVista-DR image."
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Path to a retinal fundus image.",
    )

    parser.add_argument(
        "--checkpoint",
        required=True,
        help="Path to the trained EfficientNet-B0 checkpoint.",
    )

    parser.add_argument(
        "--output",
        default="models/results/gradcam_overlay.png",
        help="Output path for the Grad-CAM overlay.",
    )

    parser.add_argument(
        "--target-class",
        type=int,
        default=None,
        help="Optional ICDR class to explain (0-4). Defaults to predicted class.",
    )

    args = parser.parse_args()

    result = explain_image(
        image_path=args.image,
        checkpoint_path=args.checkpoint,
        target_class=args.target_class,
    )

    save_explanation(
        result=result,
        output_path=args.output,
    )

    print(f"Predicted ICDR grade: {result.predicted_class}")
    print(f"Class: {result.class_name}")
    print(f"Confidence: {result.confidence:.4f}")
    print(f"Output: {args.output}")
    print()
    print("Class probabilities:")

    for class_index, probability in enumerate(result.probabilities):
        print(
            f"  Grade {class_index} "
            f"({CLASS_NAMES[class_index]}): "
            f"{probability:.4f}"
        )

    print()
    print(
        "Note: Grad-CAM highlights regions influencing the model prediction; "
        "it is not lesion-level detection."
    )


if __name__ == "__main__":
    main()