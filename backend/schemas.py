"""Pydantic schemas for the NeuroVista-DR API."""

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """ICDR classification result."""

    icdr_grade: int = Field(ge=0, le=4)
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    referable_dr: bool


class ExplainabilityResponse(BaseModel):
    """Explainability metadata."""

    gradcam_available: bool


class AnalysisResponse(BaseModel):
    """Response returned by the retinal analysis endpoint."""

    status: str
    prediction: PredictionResponse
    probabilities: dict[str, float]
    explainability: ExplainabilityResponse