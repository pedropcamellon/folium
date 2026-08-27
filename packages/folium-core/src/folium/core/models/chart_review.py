"""Serializable chart-review contracts shared by the backend and worker."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

CHARTREVIEW_WORKFLOW_NAME = "chartreview"
CHARTREVIEW_TASK_QUEUE = "chartreview-queue"


class ChartReviewSourceType(StrEnum):
    TIMELINE = "timeline"
    DOCUMENT = "document"
    INTERACTION = "interaction"
    TRANSCRIPT = "transcript"


class ChartReviewStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ChartReviewSourceChunk(BaseModel):
    source_id: str = Field(..., min_length=1, max_length=100)
    source_type: ChartReviewSourceType
    content: str = Field(..., min_length=1, max_length=20_000)
    resource_id: str | None = Field(None, min_length=1, max_length=100)
    display_label: str | None = Field(None, min_length=1, max_length=200)
    content_role: str | None = Field(None, min_length=1, max_length=100)
    occurred_at: datetime | None = None


class ChartReviewInput(BaseModel):
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
        transcript = [self.transcript] if self.transcript else []
        return [*self.timeline, *self.documents, *self.interactions, *transcript]


class ChartReviewSourceRef(BaseModel):
    source_id: str = Field(..., min_length=1, max_length=100)


class ChartReviewOutput(BaseModel):
    summary: str = Field(..., min_length=1, max_length=10_000)
    provider_name: str = Field(..., min_length=1, max_length=100)
    reasoning: str | None = Field(None, min_length=1, max_length=4_000)
    missing_info: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    source_refs: list[ChartReviewSourceRef] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)
    review_flags: list[str] = Field(default_factory=list)


class ChartReviewWorkflowInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    review_id: str = Field(..., min_length=1, max_length=100)
    review_input: ChartReviewInput
