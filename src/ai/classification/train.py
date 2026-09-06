"""Training pipeline for the NeuroVista-DR ICDR classifier."""

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

from .config import (
    BATCH_SIZE,
    CHECKPOINT_DIR,
    DATA_SPLIT_PATH,
    FREEZE_BACKBONE,
    IMAGE_SIZE,
    LEARNING_RATE,
    NUM_CLASSES,
    NUM_EPOCHS,
    NUM_WORKERS,
    PRETRAINED,
    RANDOM_SEED,
    RESULTS_DIR,
    WEIGHT_DECAY,
)
from .dataset import APTOSDataset
from .evaluate import evaluate_model, save_evaluation_results
from .model import build_model, get_device
from .preprocessing import (
    get_train_transform,
    get_validation_transform,
)


def set_seed(seed: int = RANDOM_SEED) -> None:
    """Set random seeds for reproducibility."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def calculate_class_weights(
    dataset: APTOSDataset,
) -> torch.Tensor:
    """Calculate inverse-frequency class weights."""

    counts = np.bincount(
        dataset.data["diagnosis"].to_numpy(),
        minlength=NUM_CLASSES,
    )

    if np.any(counts == 0):
        raise ValueError(
            f"Training split is missing one or more classes: {counts}"
        )

    weights = len(dataset) / (
        NUM_CLASSES * counts
    )

    return torch.tensor(
        weights,
        dtype=torch.float32,
    )


def create_dataloaders(
    batch_size: int = BATCH_SIZE,
    num_workers: int = NUM_WORKERS,
):
    """Create training and validation dataloaders."""

    train_dataset = APTOSDataset(
        DATA_SPLIT_PATH,
        split="train",
        transform=get_train_transform(IMAGE_SIZE),
    )

    validation_dataset = APTOSDataset(
        DATA_SPLIT_PATH,
        split="validation",
        transform=get_validation_transform(IMAGE_SIZE),
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    return (
        train_dataset,
        validation_dataset,
        train_loader,
        validation_loader,
    )


def train_one_batch(
    model: nn.Module,
    batch: dict,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    """Run one optimization step for smoke testing."""

    model.train()

    images = batch["image"].to(device)
    labels = batch["diagnosis"].to(device)

    optimizer.zero_grad(set_to_none=True)

    outputs = model(images)
    loss = criterion(outputs, labels)

    loss.backward()
    optimizer.step()

    return float(loss.item())


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    """Train the model for one epoch."""

    model.train()

    running_loss = 0.0
    total_samples = 0

    for batch in loader:
        images = batch["image"].to(device)
        labels = batch["diagnosis"].to(device)

        optimizer.zero_grad(set_to_none=True)

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        batch_size = images.size(0)

        running_loss += loss.item() * batch_size
        total_samples += batch_size

    return running_loss / total_samples


@torch.no_grad()
def validation_loss(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> float:
    """Calculate validation loss."""

    model.eval()

    running_loss = 0.0
    total_samples = 0

    for batch in loader:
        images = batch["image"].to(device)
        labels = batch["diagnosis"].to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        batch_size = images.size(0)

        running_loss += loss.item() * batch_size
        total_samples += batch_size

    return running_loss / total_samples


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    validation_loss_value: float,
    config: dict,
    path: Path,
) -> None:
    """Save a model checkpoint with experiment metadata."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "validation_loss": validation_loss_value,
            "config": config,
            "class_names": {
                "0": "No DR",
                "1": "Mild NPDR",
                "2": "Moderate NPDR",
                "3": "Severe NPDR",
                "4": "Proliferative DR",
            },
        },
        path,
    )


def train(
    epochs: int = NUM_EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    pretrained: bool = PRETRAINED,
    freeze_backbone: bool = FREEZE_BACKBONE,
) -> dict:
    """Run the baseline ICDR classifier training."""

    set_seed()

    device = get_device()

    print(f"Device: {device}")
    print(f"Dataset split: {DATA_SPLIT_PATH}")
    print(f"Image size: {IMAGE_SIZE}")
    print(f"Batch size: {batch_size}")
    print(f"Epochs: {epochs}")
    print(f"Pretrained: {pretrained}")
    print(f"Frozen backbone: {freeze_backbone}")

    (
        train_dataset,
        validation_dataset,
        train_loader,
        validation_loader,
    ) = create_dataloaders(
        batch_size=batch_size
    )

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(validation_dataset)}")

    class_weights = calculate_class_weights(
        train_dataset
    ).to(device)

    print(
        "Class weights:",
        class_weights.detach().cpu().numpy(),
    )

    model = build_model(
        num_classes=NUM_CLASSES,
        pretrained=pretrained,
        freeze_backbone=freeze_backbone,
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        weight=class_weights
    )

    trainable_parameters = [
        parameter
        for parameter in model.parameters()
        if parameter.requires_grad
    ]

    optimizer = AdamW(
        trainable_parameters,
        lr=learning_rate,
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=max(epochs, 2),
    )

    best_validation_loss = float("inf")

    history = {
        "config": {
            "seed": RANDOM_SEED,
            "image_size": IMAGE_SIZE,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "weight_decay": WEIGHT_DECAY,
            "epochs": epochs,
            "pretrained": pretrained,
            "freeze_backbone": freeze_backbone,
            "optimizer": "AdamW",
            "scheduler": "CosineAnnealingLR",
            "dataset_split": str(DATA_SPLIT_PATH),
            "device": str(device),
        },
        "epochs": [],
    }

    for epoch in range(1, epochs + 1):

        # -------------------------
        # Training
        # -------------------------

        train_loss = train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device,
        )

        # -------------------------
        # Validation loss
        # -------------------------

        val_loss = validation_loss(
            model,
            validation_loader,
            criterion,
            device,
        )

        # -------------------------
        # Validation metrics
        # -------------------------

        evaluation = evaluate_model(
            model=model,
            loader=validation_loader,
            device=device,
            referable_threshold=2,
        )

        scheduler.step()

        current_lr = optimizer.param_groups[0]["lr"]

        classification = evaluation["classification"]
        referable = evaluation["referable_dr"]

        print(
            f"\nEpoch {epoch}/{epochs}"
        )

        print(
            f"  train_loss: {train_loss:.4f}"
        )

        print(
            f"  val_loss:   {val_loss:.4f}"
        )

        print(
            f"  accuracy:   {classification['accuracy']:.4f}"
        )

        print(
            f"  macro_f1:   {classification['macro_f1']:.4f}"
        )

        print(
            f"  referable sensitivity: "
            f"{referable['sensitivity']:.4f}"
        )

        print(
            f"  referable specificity: "
            f"{referable['specificity']:.4f}"
        )

        print(
            f"  learning_rate: {current_lr:.6f}"
        )

        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "validation_loss": val_loss,
            "learning_rate": current_lr,
            "evaluation": evaluation,
        }

        history["epochs"].append(epoch_record)

        # -------------------------
        # Save best checkpoint
        # -------------------------

        if val_loss < best_validation_loss:
            best_validation_loss = val_loss

            save_checkpoint(
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                validation_loss_value=val_loss,
                config=history["config"],
                path=CHECKPOINT_DIR
                / "efficientnet_b0_best.pt",
            )

            save_evaluation_results(
                evaluation,
                RESULTS_DIR
                / "best_validation_metrics.json",
            )

            print(
                "  ✓ Best checkpoint updated"
            )

    # -------------------------
    # Save complete history
    # -------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    history_path = (
        RESULTS_DIR / "training_history.json"
    )

    with history_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            history,
            file,
            indent=2,
        )

    print(
        f"\nBest checkpoint:"
        f"\n  {CHECKPOINT_DIR / 'efficientnet_b0_best.pt'}"
    )

    print(
        f"Training history:"
        f"\n  {history_path}"
    )

    print(
        f"Best validation metrics:"
        f"\n  {RESULTS_DIR / 'best_validation_metrics.json'}"
    )

    return history


def parse_args():
    """Parse command-line training arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Train the NeuroVista-DR "
            "EfficientNet-B0 ICDR classifier."
        )
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=NUM_EPOCHS,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=LEARNING_RATE,
    )

    parser.add_argument(
        "--no-pretrained",
        action="store_true",
    )

    parser.add_argument(
        "--unfreeze-backbone",
        action="store_true",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        pretrained=not args.no_pretrained,
        freeze_backbone=not args.unfreeze_backbone,
    )