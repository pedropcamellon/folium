"""API contracts for X-ray review requests and results."""

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class XrayScanStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class XrayScanCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    patient_id: UUID = Field(..., alias="patientId")
    clinical_document_id: UUID = Field(..., alias="clinicalDocumentId")


class XrayFinding(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    score: float = Field(..., ge=0, le=1)


class XrayAnalysisResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    findings: list[XrayFinding]
    model_repository: str = Field(..., alias="modelRepository")
    model_revision: str = Field(..., alias="modelRevision")
    review_required: Literal[True] = Field(..., alias="reviewRequired")
    disclaimer: str


class XrayScanResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    patient_id: UUID = Field(..., alias="patientId")
    clinical_document_id: UUID = Field(..., alias="clinicalDocumentId")
    status: XrayScanStatus
    result: dict[str, Any] | None = None
    failure_message: str | None = Field(None, alias="failureMessage")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
