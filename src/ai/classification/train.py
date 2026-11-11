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
    IDRID_SPLIT_PATH,
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
from .idrid_dataset import IDRiDDataset

from .evaluate import (
    evaluate_model,
    save_evaluation_results,
)

from .model import build_model, get_device

from .preprocessing import (
    get_train_transform,
    get_validation_transform,
)


# --------------------------------------------------
# Reproducibility
# --------------------------------------------------

def set_seed(seed: int = RANDOM_SEED) -> None:
    """Set random seeds for reproducibility."""

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# --------------------------------------------------
# Dataset selection
# --------------------------------------------------

def get_dataset_class(dataset_name: str):
    """Return the dataset class for the selected dataset."""

    dataset_name = dataset_name.lower()

    if dataset_name == "aptos":
        return APTOSDataset

    if dataset_name == "idrid":
        return IDRiDDataset

    raise ValueError(
        "Unsupported dataset. Choose 'aptos' or 'idrid'."
    )


def get_dataset_path(dataset_name: str) -> Path:
    """Return the split CSV path for the selected dataset."""

    dataset_name = dataset_name.lower()

    if dataset_name == "aptos":
        return DATA_SPLIT_PATH

    if dataset_name == "idrid":
        return IDRID_SPLIT_PATH

    raise ValueError(
        "Unsupported dataset. Choose 'aptos' or 'idrid'."
    )


# --------------------------------------------------
# Class weights
# --------------------------------------------------

def calculate_class_weights(dataset) -> torch.Tensor:
    """Calculate inverse-frequency class weights."""

    labels = dataset.data["diagnosis"].to_numpy(
        dtype=int
    )

    counts = np.bincount(
        labels,
        minlength=NUM_CLASSES,
    )

    if np.any(counts == 0):
        raise ValueError(
            "Training split is missing one or more classes: "
            f"{counts.tolist()}"
        )

    weights = len(dataset) / (
        NUM_CLASSES * counts
    )

    return torch.tensor(
        weights,
        dtype=torch.float32,
    )


# --------------------------------------------------
# DataLoaders
# --------------------------------------------------

def create_dataloaders(
    batch_size: int = BATCH_SIZE,
    num_workers: int = NUM_WORKERS,
    dataset_name: str = "idrid",
):
    """Create training and validation DataLoaders."""

    dataset_name = dataset_name.lower()

    dataset_class = get_dataset_class(
        dataset_name
    )

    dataset_path = get_dataset_path(
        dataset_name
    )

    print(
        f"Loading dataset: {dataset_name.upper()}"
    )

    print(
        f"Dataset split: {dataset_path}"
    )

    # Training dataset

    train_dataset = dataset_class(
        dataset_path,
        split="train",
        transform=get_train_transform(
            IMAGE_SIZE
        ),
    )

    # Validation dataset

    validation_dataset = dataset_class(
        dataset_path,
        split="validation",
        transform=get_validation_transform(
            IMAGE_SIZE
        ),
    )

    # Training DataLoader

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    # Validation DataLoader

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


# --------------------------------------------------
# Train one batch
# --------------------------------------------------

def train_one_batch(
    model: nn.Module,
    batch: dict,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    """Run one optimization step."""

    model.train()

    images = batch["image"].to(device)

    labels = batch["diagnosis"].to(device)

    optimizer.zero_grad(
        set_to_none=True
    )

    outputs = model(images)

    loss = criterion(
        outputs,
        labels,
    )

    loss.backward()

    optimizer.step()

    return float(loss.item())


# --------------------------------------------------
# Training epoch
# --------------------------------------------------

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

        optimizer.zero_grad(
            set_to_none=True
        )

        outputs = model(images)

        loss = criterion(
            outputs,
            labels,
        )

        loss.backward()

        optimizer.step()

        batch_size = images.size(0)

        running_loss += (
            loss.item() * batch_size
        )

        total_samples += batch_size

    if total_samples == 0:
        raise ValueError(
            "Training DataLoader contains no samples."
        )

    return running_loss / total_samples


# --------------------------------------------------
# Validation loss
# --------------------------------------------------

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

        loss = criterion(
            outputs,
            labels,
        )

        batch_size = images.size(0)

        running_loss += (
            loss.item() * batch_size
        )

        total_samples += batch_size

    if total_samples == 0:
        raise ValueError(
            "Validation DataLoader contains no samples."
        )

    return running_loss / total_samples


# --------------------------------------------------
# Save checkpoint
# --------------------------------------------------

def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    validation_loss_value: float,
    config: dict,
    path: Path,
) -> None:
    """Save model checkpoint and metadata."""

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


# --------------------------------------------------
# Main training pipeline
# --------------------------------------------------

def train(
    epochs: int = NUM_EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    pretrained: bool = PRETRAINED,
    freeze_backbone: bool = FREEZE_BACKBONE,
    dataset_name: str = "idrid",
) -> dict:
    """Train and evaluate the ICDR classifier."""

    dataset_name = dataset_name.lower()

    if epochs < 1:
        raise ValueError(
            "Epochs must be greater than zero."
        )

    if batch_size < 1:
        raise ValueError(
            "Batch size must be greater than zero."
        )

    if learning_rate <= 0:
        raise ValueError(
            "Learning rate must be greater than zero."
        )

    dataset_path = get_dataset_path(
        dataset_name
    )

    set_seed()

    device = get_device()

    print("=" * 50)

    print("NeuroVista-DR Training")

    print("=" * 50)

    print(
        f"Dataset: {dataset_name.upper()}"
    )

    print(
        f"Device: {device}"
    )

    print(
        f"Dataset split: {dataset_path}"
    )

    print(
        f"Image size: {IMAGE_SIZE}"
    )

    print(
        f"Batch size: {batch_size}"
    )

    print(
        f"Epochs: {epochs}"
    )

    print(
        f"Learning rate: {learning_rate}"
    )

    print(
        f"Pretrained: {pretrained}"
    )

    print(
        f"Frozen backbone: {freeze_backbone}"
    )

    # ----------------------------------------------
    # Load datasets
    # ----------------------------------------------

    (
        train_dataset,
        validation_dataset,
        train_loader,
        validation_loader,
    ) = create_dataloaders(
        batch_size=batch_size,
        dataset_name=dataset_name,
    )

    print(
        f"Training samples: "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation samples: "
        f"{len(validation_dataset)}"
    )

    # ----------------------------------------------
    # Class weights
    # ----------------------------------------------

    class_weights = calculate_class_weights(
        train_dataset
    ).to(device)

    print(
        "Class weights:",
        class_weights.detach().cpu().numpy(),
    )

    # ----------------------------------------------
    # Build model
    # ----------------------------------------------

    model = build_model(
        num_classes=NUM_CLASSES,
        pretrained=pretrained,
        freeze_backbone=freeze_backbone,
    ).to(device)

    # ----------------------------------------------
    # Loss function
    # ----------------------------------------------

    criterion = nn.CrossEntropyLoss(
        weight=class_weights
    )

    # ----------------------------------------------
    # Optimizer
    # ----------------------------------------------

    trainable_parameters = [
        parameter
        for parameter in model.parameters()
        if parameter.requires_grad
    ]

    if not trainable_parameters:
        raise ValueError(
            "Model has no trainable parameters."
        )

    optimizer = AdamW(
        trainable_parameters,
        lr=learning_rate,
        weight_decay=WEIGHT_DECAY,
    )

    # ----------------------------------------------
    # Learning rate scheduler
    # ----------------------------------------------

    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=max(epochs, 2),
    )

    # ----------------------------------------------
    # Output paths
    # ----------------------------------------------

    checkpoint_path = (
        CHECKPOINT_DIR
        / f"efficientnet_b0_{dataset_name}_best.pt"
    )

    metrics_path = (
        RESULTS_DIR
        / f"{dataset_name}_best_validation_metrics.json"
    )

    history_path = (
        RESULTS_DIR
        / f"{dataset_name}_training_history.json"
    )

    # ----------------------------------------------
    # Training history
    # ----------------------------------------------

    best_validation_loss = float("inf")

    history = {
        "config": {
            "dataset": dataset_name,
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
            "dataset_split": str(dataset_path),
            "device": str(device),
        },
        "epochs": [],
    }

    # ----------------------------------------------
    # Epoch loop
    # ----------------------------------------------

    for epoch in range(
        1,
        epochs + 1,
    ):

        print(
            f"\nEpoch {epoch}/{epochs}"
        )

        # Training

        train_loss = train_one_epoch(
            model=model,
            loader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
        )

        # Validation loss

        val_loss = validation_loss(
            model=model,
            loader=validation_loader,
            criterion=criterion,
            device=device,
        )

        # Evaluation metrics

        evaluation = evaluate_model(
            model=model,
            loader=validation_loader,
            device=device,
            referable_threshold=2,
        )

        # Update learning rate

        scheduler.step()

        current_lr = optimizer.param_groups[0]["lr"]

        classification = evaluation[
            "classification"
        ]

        referable = evaluation[
            "referable_dr"
        ]

        # ------------------------------------------
        # Print metrics
        # ------------------------------------------

        print(
            f"  train_loss: "
            f"{train_loss:.4f}"
        )

        print(
            f"  val_loss: "
            f"{val_loss:.4f}"
        )

        print(
            f"  accuracy: "
            f"{classification['accuracy']:.4f}"
        )

        print(
            f"  macro_f1: "
            f"{classification['macro_f1']:.4f}"
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
            f"  learning_rate: "
            f"{current_lr:.6f}"
        )

        # ------------------------------------------
        # Save epoch history
        # ------------------------------------------

        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "validation_loss": val_loss,
            "learning_rate": current_lr,
            "evaluation": evaluation,
        }

        history["epochs"].append(
            epoch_record
        )

        # ------------------------------------------
        # Save best checkpoint
        # ------------------------------------------

        if val_loss < best_validation_loss:

            best_validation_loss = val_loss

            save_checkpoint(
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                validation_loss_value=val_loss,
                config=history["config"],
                path=checkpoint_path,
            )

            save_evaluation_results(
                evaluation,
                metrics_path,
            )

            print(
                "  Best checkpoint updated"
            )

    # ----------------------------------------------
    # Save complete training history
    # ----------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
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

    # ----------------------------------------------
    # Final output
    # ----------------------------------------------

    print(
        "\nTraining completed"
    )

    print(
        f"Best checkpoint:\n"
        f"  {checkpoint_path}"
    )

    print(
        f"Training history:\n"
        f"  {history_path}"
    )

    print(
        f"Best validation metrics:\n"
        f"  {metrics_path}"
    )

    return history


# --------------------------------------------------
# Command-line arguments
# --------------------------------------------------

def parse_args():
    """Parse command-line training arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Train the NeuroVista-DR "
            "EfficientNet-B0 ICDR classifier."
        )
    )

    parser.add_argument(
        "--dataset",
        choices=[
            "aptos",
            "idrid",
        ],
        default="idrid",
        help="Dataset to train on.",
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


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":

    args = parse_args()

    train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        pretrained=not args.no_pretrained,
        freeze_backbone=not args.unfreeze_backbone,
        dataset_name=args.dataset,
    )