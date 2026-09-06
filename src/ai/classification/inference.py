"""Single-image inference for the NeuroVista-DR ICDR classifier."""

import argparse
from pathlib import Path

import torch
from PIL import Image

from .config import CLASS_NAMES, IMAGE_SIZE, NUM_CLASSES
from .model import build_model, get_device
from .preprocessing import get_validation_transform


def load_checkpoint(
    checkpoint_path: str | Path,
    device: torch.device | None = None,
):
    """Load a trained EfficientNet-B0 checkpoint."""

    if device is None:
        device = get_device()

    checkpoint_path = Path(checkpoint_path)

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}"
        )

    model = build_model(
        num_classes=NUM_CLASSES,
        pretrained=False,
        freeze_backbone=False,
    )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    return model


@torch.no_grad()
def predict(
    image_path: str | Path,
    checkpoint_path: str | Path,
) -> dict:
    """Predict ICDR grade for a single fundus image."""

    device = get_device()

    model = load_checkpoint(
        checkpoint_path,
        device,
    )

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = Image.open(image_path).convert("RGB")

    transform = get_validation_transform(
        IMAGE_SIZE
    )

    tensor = transform(image).unsqueeze(0).to(device)

    logits = model(tensor)

    probabilities = torch.softmax(
        logits,
        dim=1,
    )[0]

    predicted_grade = int(
        torch.argmax(probabilities).item()
    )

    return {
        "predicted_grade": predicted_grade,
        "predicted_class": CLASS_NAMES[predicted_grade],
        "confidence": float(
            probabilities[predicted_grade].item()
        ),
        "probabilities": {
            str(index): float(
                probabilities[index].item()
            )
            for index in range(NUM_CLASSES)
        },
        "device": str(device),
    }


def parse_args():
    """Parse command-line inference arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Run NeuroVista-DR ICDR inference "
            "on a single fundus image."
        )
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Path to the fundus image.",
    )

    parser.add_argument(
        "--checkpoint",
        required=True,
        help="Path to the trained model checkpoint.",
    )

    return parser.parse_args()


def main():
    """Run command-line inference."""

    args = parse_args()

    result = predict(
        image_path=args.image,
        checkpoint_path=args.checkpoint,
    )

    print("\nNeuroVista-DR Prediction")
    print("------------------------")
    print(
        f"Predicted ICDR grade: "
        f"{result['predicted_grade']}"
    )
    print(
        f"Classification: "
        f"{result['predicted_class']}"
    )
    print(
        f"Confidence: "
        f"{result['confidence']:.4f}"
    )
    print(
        f"Device: "
        f"{result['device']}"
    )

    print("\nClass probabilities:")

    for grade, probability in result[
        "probabilities"
    ].items():
        print(
            f"  Grade {grade}: "
            f"{probability:.4f}"
        )


if __name__ == "__main__":
    main()