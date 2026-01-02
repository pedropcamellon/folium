"""Pydantic models for summarization service."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """Request schema for summarization endpoint."""

    transcript: str = Field(..., description="Clinical transcript text to summarize")
    interaction_type: Optional[str] = Field(
        None,
        description="Type of clinical interaction (e.g., 'consultation', 'follow-up')",
    )
    format: Optional[str] = Field(
        "soap", description="Output format: 'soap' (default), 'narrative', 'structured'"
    )
    language: Optional[str] = Field("en", description="Language code (default: 'en')")

    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "Patient reports chest pain for 2 days. Pain is sharp, worse with deep breathing. No fever. Vital signs stable. Heart sounds normal. Likely costochondritis. Plan: NSAIDs, follow-up in 1 week if not improved.",
                "interaction_type": "consultation",
                "format": "soap",
                "language": "en",
            }
        }


class StructuredSummary(BaseModel):
    """Structured clinical summary data (SOAP format)."""

    chief_complaint: Optional[str] = Field(
        None, description="Brief reason for visit/interaction"
    )
    subjective: Optional[str] = Field(
        None, description="Patient's description of symptoms, history, concerns"
    )
    objective: Optional[str] = Field(
        None, description="Observable findings, vitals, exam results"
    )
    assessment: Optional[str] = Field(
        None, description="Clinical impression, diagnosis, differential"
    )
    plan: Optional[str | List[str]] = Field(
        None,
        description="Treatment plan, medications, follow-up, education (string or list)",
    )
    clinical_tags: List[str] = Field(
        default_factory=list,
        description="Relevant medical tags (e.g., 'hypertension', 'diabetes')",
    )
    icd_codes: List[str] = Field(
        default_factory=list, description="Suggested ICD-10 codes"
    )
    action_items: List[str] = Field(
        default_factory=list,
        description="Follow-up actions (labs, referrals, prescriptions)",
    )


class SummarizeResponse(BaseModel):
    """Response schema for summarization endpoint."""

    summary: str = Field(..., description="Full narrative summary")
    structured_data: StructuredSummary = Field(
        ..., description="Structured clinical data in SOAP format"
    )
    processing_time: float = Field(..., description="Processing time in seconds")
    model_used: str = Field(..., description="Name of the model used")
    provider: str = Field(..., description="Provider name (local, openai, etc.)")
    usage: Optional[Dict[str, Any]] = Field(
        None, description="Token usage and cost information (if applicable)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Patient presenting with chest pain likely due to costochondritis. Vital signs stable. Plan includes NSAIDs and follow-up.",
                "structured_data": {
                    "chief_complaint": "Chest pain for 2 days",
                    "subjective": "Patient reports sharp pain, worse with deep breathing. No fever.",
                    "objective": "Vital signs stable. Heart sounds normal.",
                    "assessment": "Likely costochondritis",
                    "plan": "NSAIDs, follow-up in 1 week if not improved",
                    "clinical_tags": ["chest-pain", "costochondritis"],
                    "icd_codes": ["M94.0"],
                    "action_items": [
                        "Prescribe NSAIDs",
                        "Schedule follow-up in 1 week",
                    ],
                },
                "processing_time": 3.45,
                "model_used": "llama-3-8b-instruct",
                "provider": "local",
                "usage": None,
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    provider: str = Field(..., description="Active provider name")
    model: str = Field(..., description="Model name")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    model_used: Optional[str] = Field(None, description="Model name if available")
