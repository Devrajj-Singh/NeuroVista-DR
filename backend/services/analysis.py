"""AI analysis service for the NeuroVista-DR backend."""

from __future__ import annotations

import base64
import io
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from backend.services.quality import QualityResult, assess_quality
from src.ai.classification.config import (
    CLASS_NAMES,
    IMAGE_SIZE,
    REFERABLE_DR_THRESHOLD,
)
from src.ai.classification.model import build_model, get_device
from src.ai.classification.preprocessing import get_validation_transform
from src.ai.explainability.gradcam import GradCAM, create_overlay


def heatmap_to_data_url(overlay: np.ndarray) -> str:
    """Encode an RGB overlay array as a PNG data URL for the frontend."""
    image = Image.fromarray(overlay.astype(np.uint8))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


class AnalysisService:
    """Loads and runs the NeuroVista-DR AI models.

    The classification model is loaded once when the service is created
    instead of being reloaded for every API request.

    The service first runs an image-quality gate. If an image is rejected
    as ungradable, classification and Grad-CAM are **not** executed.
    """

    def __init__(
        self,
        checkpoint_path: str | Path,
        device: torch.device | None = None,
    ) -> None:
        self.checkpoint_path = Path(checkpoint_path)
        self.device = device or get_device()

        if not self.checkpoint_path.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found: {self.checkpoint_path}"
            )

        self.model = build_model(
            pretrained=False,
            freeze_backbone=False,
        )

        checkpoint = torch.load(
            self.checkpoint_path,
            map_location=self.device,
            weights_only=True,
        )

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        else:
            state_dict = checkpoint

        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        # Final convolutional feature stage used by Grad-CAM.
        self.gradcam = GradCAM(
            model=self.model,
            target_layer=self.model.features[8],
            device=self.device,
        )

        self.transform = get_validation_transform(IMAGE_SIZE)

    def _prepare_image(self, image: Image.Image) -> torch.Tensor:
        """Convert a PIL image into a model input tensor."""
        image = image.convert("RGB")

        tensor = self.transform(image)

        return tensor.unsqueeze(0)

    def analyze(
        self,
        image: Image.Image,
    ) -> dict:
        """Run the quality gate, then ICDR classification and Grad-CAM.

        Returns a dict matching the API contract. When the image is
        rejected, the result carries ``status="ungradable"`` with a quality
        reason and no prediction/explainability.
        """
        # 1. Quality gate — reject before any classification.
        quality: QualityResult = assess_quality(image)

        if quality.status == "ungradable":
            return {
                "status": "ungradable",
                "quality": {
                    "status": "ungradable",
                    "reason": quality.reason,
                },
                "prediction": None,
                "probabilities": None,
                "explainability": None,
            }

        # 2. Preprocessing.
        input_tensor = self._prepare_image(image)

        # 3. DR classification + Grad-CAM.
        heatmap, _, probabilities = self.gradcam.generate(
            input_tensor=input_tensor,
        )

        predicted_class = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_class])

        probability_dict = {
            str(class_index): float(probability)
            for class_index, probability in enumerate(probabilities)
        }

        # 4. Referable DR decision.
        referable = predicted_class >= REFERABLE_DR_THRESHOLD

        # 5. Visual Grad-CAM overlay, returned to the frontend.
        overlay = create_overlay(
            image=image.convert("RGB"),
            heatmap=heatmap,
            alpha=0.4,
        )
        heatmap_image = heatmap_to_data_url(overlay)

        return {
            "status": "success",
            "quality": {
                "status": "good",
                "reason": None,
            },
            "prediction": {
                "icdr_grade": predicted_class,
                "class_name": CLASS_NAMES[predicted_class],
                "confidence": confidence,
                "referable_dr": referable,
            },
            "probabilities": probability_dict,
            "explainability": {
                "gradcam_available": True,
                "heatmap_image": heatmap_image,
            },
        }
