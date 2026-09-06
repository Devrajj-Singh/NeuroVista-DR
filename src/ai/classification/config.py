"""Configuration for the NeuroVista-DR baseline ICDR classifier."""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_SPLIT_PATH = PROJECT_ROOT / "data" / "splits" / "aptos_split.csv"

CHECKPOINT_DIR = PROJECT_ROOT / "models" / "checkpoints"
RESULTS_DIR = PROJECT_ROOT / "models" / "results"

CLASS_NAMES = {
    0: "No DR",
    1: "Mild NPDR",
    2: "Moderate NPDR",
    3: "Severe NPDR",
    4: "Proliferative DR",
}

NUM_CLASSES = len(CLASS_NAMES)

RANDOM_SEED = 42

IMAGE_SIZE = 224
BATCH_SIZE = 16
NUM_WORKERS = 0

LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
NUM_EPOCHS = 10

PRETRAINED = True
FREEZE_BACKBONE = True

OPTIMIZER = "adamw"
SCHEDULER = "cosine"

REFERABLE_DR_THRESHOLD = 2


@dataclass(frozen=True)
class TrainingConfig:
    """Baseline training configuration."""

    image_size: int = IMAGE_SIZE
    batch_size: int = BATCH_SIZE
    num_workers: int = NUM_WORKERS

    learning_rate: float = LEARNING_RATE
    weight_decay: float = WEIGHT_DECAY
    epochs: int = NUM_EPOCHS

    pretrained: bool = PRETRAINED
    freeze_backbone: bool = FREEZE_BACKBONE

    optimizer: str = OPTIMIZER
    scheduler: str = SCHEDULER

    random_seed: int = RANDOM_SEED