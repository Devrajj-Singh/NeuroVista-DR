"""APTOS dataset loader for NeuroVista-DR ICDR classification."""

from pathlib import Path

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


VALID_SPLITS = {"train", "validation"}
VALID_GRADES = {0, 1, 2, 3, 4}


class APTOSDataset(Dataset):
    """PyTorch dataset backed by the verified APTOS split CSV."""

    def __init__(
        self,
        split_csv: str | Path,
        split: str,
        transform=None,
    ) -> None:
        if split not in VALID_SPLITS:
            raise ValueError(
                f"Invalid split '{split}'. "
                f"Expected one of: {sorted(VALID_SPLITS)}"
            )

        self.split_csv = Path(split_csv)
        self.project_root = self.split_csv.resolve().parents[2]
        self.transform = transform

        if not self.split_csv.exists():
            raise FileNotFoundError(
                f"Split file not found: {self.split_csv}"
            )

        self.data = pd.read_csv(self.split_csv)

        required_columns = {
            "image_id",
            "filename",
            "relative_path",
            "sha256",
            "diagnosis",
            "split",
            "duplicate_status",
        }

        missing_columns = required_columns - set(self.data.columns)

        if missing_columns:
            raise ValueError(
                f"Split CSV is missing required columns: "
                f"{sorted(missing_columns)}"
            )

        # Only use the requested model-development split.
        self.data = self.data[self.data["split"] == split].copy()

        # Duplicate records are never allowed into model development.
        self.data = self.data[
            self.data["duplicate_status"] == "unique"
        ].copy()

        if self.data.empty:
            raise ValueError(
                f"No valid records found for split '{split}'."
            )

        self.data["diagnosis"] = self.data["diagnosis"].astype(int)

        invalid_grades = set(self.data["diagnosis"]) - VALID_GRADES

        if invalid_grades:
            raise ValueError(
                f"Invalid diagnosis values found: "
                f"{sorted(invalid_grades)}"
            )

        self.data.reset_index(drop=True, inplace=True)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int):
        row = self.data.iloc[index]

        image_path = self.project_root / Path(row["relative_path"])

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found for {row['image_id']}: "
                f"{image_path}"
            )

        image = Image.open(image_path).convert("RGB")
        diagnosis = int(row["diagnosis"])

        if self.transform is not None:
            image = self.transform(image)

        return {
            "image": image,
            "diagnosis": diagnosis,
            "image_id": row["image_id"],
            "filename": row["filename"],
        }