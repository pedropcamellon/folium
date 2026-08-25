"""Validated contracts for synthetic chart-review draft support."""

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ChartReviewSourceType(str, Enum):
    """Supported sources for a chart-review context bundle."""

    TIMELINE = "timeline"
    DOCUMENT = "document"
    INTERACTION = "interaction"
    TRANSCRIPT = "transcript"


class ChartReviewSourceChunk(BaseModel):
    """A traceable synthetic input record supplied to the review agent."""

    source_id: str = Field(..., min_length=1, max_length=100)
    source_type: ChartReviewSourceType
    content: str = Field(..., min_length=1, max_length=20_000)


class ChartReviewInput(BaseModel):
    """Synthetic patient context used to create a bounded draft review."""

    patient_id: str = Field(..., min_length=1, max_length=100)
    interaction_id: str = Field(..., min_length=1, max_length=100)
    timeline: list[ChartReviewSourceChunk] = Field(default_factory=list)
    documents: list[ChartReviewSourceChunk] = Field(default_factory=list)
    interactions: list[ChartReviewSourceChunk] = Field(default_factory=list)
    transcript: ChartReviewSourceChunk | None = None

    @model_validator(mode="after")
    def validate_source_ids(self) -> "ChartReviewInput":
        source_ids = [source.source_id for source in self.source_chunks]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Chart review source IDs must be unique")
        return self

    @property
    def source_chunks(self) -> list[ChartReviewSourceChunk]:
        """Return all supplied source chunks in a stable order."""
        transcript = [self.transcript] if self.transcript else []
        return [*self.timeline, *self.documents, *self.interactions, *transcript]


class ChartReviewSourceRef(BaseModel):
    """Reference to one source chunk used by a generated draft."""

    source_id: str = Field(..., min_length=1, max_length=100)


class ChartReviewOutput(BaseModel):
    """Validated draft-support output returned by a chart-review provider."""

    summary: str = Field(..., min_length=1, max_length=10_000)
    missing_info: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    source_refs: list[ChartReviewSourceRef] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)
    review_flags: list[str] = Field(default_factory=list)
