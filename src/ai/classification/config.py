"""Configuration for NeuroVista-DR ICDR classification."""

from dataclasses import dataclass
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ============================================================
# DATASET PATHS
# ============================================================

# Existing APTOS dataset
DATA_SPLIT_PATH = (
    PROJECT_ROOT
    / "data"
    / "splits"
    / "aptos_split.csv"
)

# IDRiD dataset
IDRID_SPLIT_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "idrid_project_split.csv"
)


# ============================================================
# MODEL PATHS
# ============================================================

CHECKPOINT_DIR = (
    PROJECT_ROOT
    / "models"
    / "checkpoints"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "models"
    / "results"
)


# ============================================================
# CLASSIFICATION CONFIGURATION
# ============================================================

CLASS_NAMES = {
    0: "No DR",
    1: "Mild NPDR",
    2: "Moderate NPDR",
    3: "Severe NPDR",
    4: "Proliferative DR",
}

NUM_CLASSES = 5


# ============================================================
# REPRODUCIBILITY
# ============================================================

RANDOM_SEED = 42


# ============================================================
# IMAGE CONFIGURATION
# ============================================================

IMAGE_SIZE = 224


# ============================================================
# TRAINING CONFIGURATION
# ============================================================

BATCH_SIZE = 16

NUM_WORKERS = 0

LEARNING_RATE = 1e-4

WEIGHT_DECAY = 1e-4

NUM_EPOCHS = 10


# ============================================================
# MODEL CONFIGURATION
# ============================================================

PRETRAINED = True

FREEZE_BACKBONE = True


# ============================================================
# OPTIMIZATION CONFIGURATION
# ============================================================

OPTIMIZER = "adamw"

SCHEDULER = "cosine"


# ============================================================
# REFERABLE DR CONFIGURATION
# ============================================================

REFERABLE_DR_THRESHOLD = 2


# ============================================================
# TRAINING CONFIGURATION DATACLASS
# ============================================================

@dataclass(frozen=True)
class TrainingConfig:
    """Configuration for ICDR model training."""

    data_split_path: Path = DATA_SPLIT_PATH

    image_size: int = IMAGE_SIZE

    batch_size: int = BATCH_SIZE

    num_workers: int = NUM_WORKERS

    learning_rate: float = LEARNING_RATE

    weight_decay: float = WEIGHT_DECAY

    num_epochs: int = NUM_EPOCHS

    pretrained: bool = PRETRAINED

    freeze_backbone: bool = FREEZE_BACKBONE

    optimizer: str = OPTIMIZER

    scheduler: str = SCHEDULER

    random_seed: int = RANDOM_SEED

    num_classes: int = NUM_CLASSES

    referable_dr_threshold: int = (
        REFERABLE_DR_THRESHOLD
    )