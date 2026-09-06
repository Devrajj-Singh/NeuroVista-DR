"""FastAPI application for the NeuroVista-DR prototype."""

from __future__ import annotations

import io
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from backend.schemas import AnalysisResponse
from backend.services.analysis import AnalysisService


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CHECKPOINT = (
    PROJECT_ROOT
    / "models"
    / "checkpoints"
    / "efficientnet_b0_best.pt"
)

CHECKPOINT_PATH = Path(
    os.getenv(
        "NEUROVISTA_MODEL_CHECKPOINT",
        str(DEFAULT_CHECKPOINT),
    )
)


app = FastAPI(
    title="NeuroVista-DR API",
    description="Prototype API for explainable diabetic retinopathy screening.",
    version="0.1.0",
)


analysis_service: AnalysisService | None = None


@app.on_event("startup")
def load_models() -> None:
    """Load AI models once when the API starts."""
    global analysis_service

    try:
        analysis_service = AnalysisService(
            checkpoint_path=CHECKPOINT_PATH,
        )
    except FileNotFoundError as exc:
        # Keep the API available for health checks even when the
        # local model checkpoint is unavailable.
        print(f"WARNING: {exc}")
        analysis_service = None


@app.get("/api/v1/health")
def health_check() -> dict:
    """Return backend and model availability."""
    return {
        "status": "ok",
        "service": "neurovista-dr-api",
        "model_loaded": analysis_service is not None,
    }


@app.post(
    "/api/v1/analyze",
    response_model=AnalysisResponse,
)
async def analyze_fundus(
    image: UploadFile = File(...),
) -> AnalysisResponse:
    """Analyze an uploaded retinal fundus image."""

    if analysis_service is None:
        raise HTTPException(
            status_code=503,
            detail="AI model is not available.",
        )

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image.",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        pil_image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image.",
        ) from exc

    try:
        result = analysis_service.analyze(pil_image)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Image analysis failed.",
        ) from exc

    # Do not expose internal NumPy heatmap data through the API contract.
    result.pop("_heatmap", None)

    return AnalysisResponse(**result)