"""Evaluation utilities for the NeuroVista-DR ICDR classifier."""

from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader


ICDR_LABELS = [0, 1, 2, 3, 4]


def calculate_classification_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
) -> dict:
    """Calculate multiclass ICDR 0-4 classification metrics."""

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    report = classification_report(
        y_true,
        y_pred,
        labels=ICDR_LABELS,
        output_dict=True,
        zero_division=0,
    )

    return {
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),
        "macro_precision": float(
            precision_score(
                y_true,
                y_pred,
                labels=ICDR_LABELS,
                average="macro",
                zero_division=0,
            )
        ),
        "macro_recall": float(
            recall_score(
                y_true,
                y_pred,
                labels=ICDR_LABELS,
                average="macro",
                zero_division=0,
            )
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                labels=ICDR_LABELS,
                average="macro",
                zero_division=0,
            )
        ),
        "per_class": {
            str(label): {
                "precision": float(
                    report[str(label)]["precision"]
                ),
                "recall": float(
                    report[str(label)]["recall"]
                ),
                "f1": float(
                    report[str(label)]["f1-score"]
                ),
                "support": int(
                    report[str(label)]["support"]
                ),
            }
            for label in ICDR_LABELS
        },
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred,
            labels=ICDR_LABELS,
        ).tolist(),
    }


def calculate_referable_dr_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    threshold: int = 2,
) -> dict:
    """
    Calculate binary referable-DR metrics.

    Referable DR is defined as ICDR >= threshold.
    """

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    true_referable = y_true >= threshold
    pred_referable = y_pred >= threshold

    true_positive = int(
        np.sum(true_referable & pred_referable)
    )
    true_negative = int(
        np.sum(~true_referable & ~pred_referable)
    )
    false_positive = int(
        np.sum(~true_referable & pred_referable)
    )
    false_negative = int(
        np.sum(true_referable & ~pred_referable)
    )

    sensitivity = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative > 0
        else 0.0
    )

    specificity = (
        true_negative / (true_negative + false_positive)
        if true_negative + false_positive > 0
        else 0.0
    )

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive > 0
        else 0.0
    )

    recall = sensitivity

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return {
        "threshold": threshold,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


@torch.no_grad()
def collect_predictions(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> tuple[list[int], list[int], list[float]]:
    """Run inference over a dataloader and collect predictions."""

    model.eval()

    y_true: list[int] = []
    y_pred: list[int] = []
    confidences: list[float] = []

    for batch in loader:
        images = batch["image"].to(device)
        labels = batch["diagnosis"].to(device)

        logits = model(images)
        probabilities = torch.softmax(logits, dim=1)

        predictions = torch.argmax(
            probabilities,
            dim=1,
        )

        batch_confidences = torch.max(
            probabilities,
            dim=1,
        ).values

        y_true.extend(
            labels.cpu().tolist()
        )

        y_pred.extend(
            predictions.cpu().tolist()
        )

        confidences.extend(
            batch_confidences.cpu().tolist()
        )

    return y_true, y_pred, confidences


@torch.no_grad()
def evaluate_model(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    referable_threshold: int = 2,
) -> dict:
    """Evaluate a trained model on a dataset."""

    y_true, y_pred, confidences = collect_predictions(
        model,
        loader,
        device,
    )

    classification_metrics = (
        calculate_classification_metrics(
            y_true,
            y_pred,
        )
    )

    referable_metrics = (
        calculate_referable_dr_metrics(
            y_true,
            y_pred,
            threshold=referable_threshold,
        )
    )

    return {
        "classification": classification_metrics,
        "referable_dr": referable_metrics,
        "confidence": {
            "mean": float(np.mean(confidences)),
            "minimum": float(np.min(confidences)),
            "maximum": float(np.max(confidences)),
        },
        "num_samples": len(y_true),
    }


def save_evaluation_results(
    results: dict,
    output_path: str | Path,
) -> None:
    """Save evaluation results as JSON."""

    import json

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )