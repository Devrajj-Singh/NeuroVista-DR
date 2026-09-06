"""AI analysis service for the NeuroVista-DR backend."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image

from src.ai.classification.config import (
    CLASS_NAMES,
    IMAGE_SIZE,
    REFERABLE_DR_THRESHOLD,
)
from src.ai.classification.model import build_model, get_device
from src.ai.classification.preprocessing import get_validation_transform
from src.ai.explainability.gradcam import GradCAM


class AnalysisService:
    """Loads and runs the NeuroVista-DR AI models.

    The classification model is loaded once when the service is created
    instead of being reloaded for every API request.
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
        """Run ICDR classification and Grad-CAM analysis."""

        input_tensor = self._prepare_image(image)

        heatmap, _, probabilities = self.gradcam.generate(
            input_tensor=input_tensor,
        )

        predicted_class = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_class])

        probability_dict = {
            str(class_index): float(probability)
            for class_index, probability in enumerate(probabilities)
        }

        return {
            "status": "success",
            "prediction": {
                "icdr_grade": predicted_class,
                "class_name": CLASS_NAMES[predicted_class],
                "confidence": confidence,
                "referable_dr": predicted_class >= REFERABLE_DR_THRESHOLD,
            },
            "probabilities": probability_dict,
            "explainability": {
                "gradcam_available": True,
            },
            # Keep this available internally for the next stage.
            "_heatmap": heatmap,
        }