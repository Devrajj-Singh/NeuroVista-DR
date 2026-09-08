"""Pydantic schemas for the NeuroVista-DR API."""

from pydantic import BaseModel, Field


class QualityResponse(BaseModel):
    """Image-quality verdict."""

    status: str
    reason: str | None = None


class PredictionResponse(BaseModel):
    """ICDR classification result."""

    icdr_grade: int = Field(ge=0, le=4)
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    referable_dr: bool


class ExplainabilityResponse(BaseModel):
    """Explainability metadata and image."""

    gradcam_available: bool
    # Data URL of the Grad-CAM overlay PNG (only when available).
    heatmap_image: str | None = None


class AnalysisResponse(BaseModel):
    """Response returned by the retinal analysis endpoint."""

    status: str
    quality: QualityResponse
    prediction: PredictionResponse | None = None
    probabilities: dict[str, float] | None = None
    explainability: ExplainabilityResponse | None = None
