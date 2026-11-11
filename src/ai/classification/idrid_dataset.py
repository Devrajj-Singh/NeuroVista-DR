"""IDRiD dataset loader for NeuroVista-DR diabetic retinopathy classification."""

from pathlib import Path

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


VALID_SPLITS = {"train", "validation"}
VALID_GRADES = {0, 1, 2, 3, 4}


class IDRiDDataset(Dataset):
    """
    PyTorch dataset backed by the verified IDRiD project split.

    Returns:
        image: Transformed image tensor.
        diagnosis: Diabetic retinopathy grade (0-4).
        image_id: IDRiD image identifier.
        filename: Image filename.
    """

    def __init__(
        self,
        split_csv: str | Path,
        split: str,
        transform=None,
    ) -> None:

        # Validate requested split
        if split not in VALID_SPLITS:
            raise ValueError(
                f"Invalid split '{split}'. "
                f"Expected one of {VALID_SPLITS}."
            )

        self.split_csv = Path(split_csv)

        # Project root is three levels above the split CSV directory
        self.project_root = self.split_csv.resolve().parents[2]

        self.transform = transform

        # Check whether split CSV exists
        if not self.split_csv.exists():
            raise FileNotFoundError(
                f"IDRiD split CSV not found: {self.split_csv}"
            )

        # Load split metadata
        self.data = pd.read_csv(self.split_csv)

        # Required metadata columns
        required_columns = {
            "image_id",
            "path",
            "retinopathy_grade",
            "project_split",
        }

        missing_columns = required_columns - set(self.data.columns)

        if missing_columns:
            raise ValueError(
                f"IDRiD split CSV is missing required columns: "
                f"{missing_columns}"
            )

        # Keep only requested split
        self.data = self.data[
            self.data["project_split"] == split
        ].copy()

        if self.data.empty:
            raise ValueError(
                f"No IDRiD images found for split '{split}'."
            )

        # Convert retinopathy grades to integers
        self.data["retinopathy_grade"] = (
            self.data["retinopathy_grade"].astype(int)
        )

        # Validate grades
        invalid_grades = (
            set(self.data["retinopathy_grade"]) - VALID_GRADES
        )

        if invalid_grades:
            raise ValueError(
                f"Invalid retinopathy grades found: {invalid_grades}"
            )

        # Use the same label column as the APTOS training pipeline.
        # This allows shared training code to access dataset.data["diagnosis"].
        self.data["diagnosis"] = self.data["retinopathy_grade"]

        # Reset dataframe index
        self.data.reset_index(drop=True, inplace=True)

    def __len__(self) -> int:
        """Return number of images in the selected split."""
        return len(self.data)

    def __getitem__(self, index: int) -> dict:
        """Load and return one image and its metadata."""

        row = self.data.iloc[index]

        # Construct image path
        image_path = self.project_root / Path(row["path"])

        # Verify image exists
        if not image_path.exists():
            raise FileNotFoundError(
                f"IDRiD image not found: {image_path}"
            )

        # Load image and convert to RGB
        image = Image.open(image_path).convert("RGB")

        # Get diagnosis label
        diagnosis = int(row["diagnosis"])

        # Apply preprocessing transformations
        if self.transform is not None:
            image = self.transform(image)

        # Return same structure expected by training pipeline
        return {
            "image": image,
            "diagnosis": diagnosis,
            "image_id": row["image_id"],
            "filename": image_path.name,
        }