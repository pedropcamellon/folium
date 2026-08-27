"""Pydantic models for summarization service."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1, max_length=40_000)


class ChatCompletionsRequest(BaseModel):
    """Subset of the OpenAI chat-completions request used by local workers."""

    model: str = Field(..., min_length=1)
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=20)
    temperature: float | None = Field(None, ge=0, le=2)
    max_tokens: int | None = Field(None, ge=1, le=4_000)
    response_format: dict[str, str] | None = None


class SummarizeRequest(BaseModel):
    """Request schema for summarization endpoint."""

    transcript: str = Field(..., description="Clinical transcript text to summarize")
    interaction_type: str | None = Field(
        None,
        description="Type of clinical interaction (e.g., 'consultation', 'follow-up')",
    )
    format: str | None = Field(
        "soap", description="Output format: 'soap' (default), 'narrative', 'structured'"
    )
    language: str | None = Field("en", description="Language code (default: 'en')")

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

    chief_complaint: str | None = Field(
        None, description="Brief reason for visit/interaction"
    )
    subjective: str | None = Field(
        None, description="Patient's description of symptoms, history, concerns"
    )
    objective: str | None = Field(
        None, description="Observable findings, vitals, exam results"
    )
    assessment: str | None = Field(
        None, description="Clinical impression, diagnosis, differential"
    )
    plan: str | None = Field(
        None,
        description="Treatment plan, medications, follow-up, education",
    )
    clinical_tags: list[str] = Field(
        default_factory=list,
        description="Relevant medical tags (e.g., 'hypertension', 'diabetes')",
    )
    icd_codes: list[str] = Field(
        default_factory=list, description="Suggested ICD-10 codes"
    )
    action_items: list[str] = Field(
        default_factory=list,
        description="Follow-up actions (labs, referrals, prescriptions)",
    )

    @field_validator(
        "chief_complaint",
        "subjective",
        "objective",
        "assessment",
        "plan",
        mode="before",
    )
    @classmethod
    def normalize_text_fields(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            normalized = [str(item).strip() for item in value if str(item).strip()]
            return "\n".join(normalized)
        if isinstance(value, dict):
            normalized = [
                f"{key}: {item}" if item not in (None, "", [], {}) else str(key)
                for key, item in value.items()
            ]
            normalized = [item.strip() for item in normalized if item.strip()]
            return "\n".join(normalized)
        return str(value)

    @field_validator("clinical_tags", "icd_codes", "action_items", mode="before")
    @classmethod
    def normalize_list_fields(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        if isinstance(value, str):
            stripped = value.strip()
            return [stripped] if stripped else []
        return [str(value)]


class SummarizeResponse(BaseModel):
    """Response schema for summarization endpoint."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
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
        },
    )

    summary: str = Field(..., description="Full narrative summary")
    structured_data: StructuredSummary = Field(
        ..., description="Structured clinical data in SOAP format"
    )
    processing_time: float = Field(..., description="Processing time in seconds")
    model_used: str = Field(..., description="Name of the model used")
    provider: str = Field(..., description="Provider name (local, openai, etc.)")
    usage: dict[str, Any] | None = Field(
        None, description="Token usage and cost information (if applicable)"
    )


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    provider: str = Field(..., description="Active provider name")
    model: str = Field(..., description="Model name")


class ErrorResponse(BaseModel):
    """Error response schema."""

    model_config = ConfigDict(protected_namespaces=())

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    model_used: str | None = Field(None, description="Model name if available")
