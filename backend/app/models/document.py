"""Clinical document data models (Pydantic)"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ClinicalDocumentType(str, Enum):
    """Types of clinical documents"""

    CLINICAL_NOTE = "ClinicalNote"
    LAB_RESULT = "LabResult"
    IMAGING_REPORT = "ImagingReport"
    PRESCRIPTION = "Prescription"
    ADMINISTRATIVE_FORM = "AdministrativeForm"
    VISIT_SUMMARY = "VisitSummary"
    PATIENT_UPLOAD = "PatientUpload"
    BILLING_CODING = "BillingCoding"
    COMMUNICATION_MESSAGE = "CommunicationMessage"


def get_type_label(doc_type: ClinicalDocumentType) -> str:
    """Convert document type to human-readable label"""
    labels = {
        ClinicalDocumentType.CLINICAL_NOTE: "Note",
        ClinicalDocumentType.LAB_RESULT: "Labs",
        ClinicalDocumentType.IMAGING_REPORT: "Imaging",
        ClinicalDocumentType.PRESCRIPTION: "Prescription",
        ClinicalDocumentType.ADMINISTRATIVE_FORM: "Form",
        ClinicalDocumentType.VISIT_SUMMARY: "Summary",
        ClinicalDocumentType.PATIENT_UPLOAD: "Upload",
        ClinicalDocumentType.BILLING_CODING: "Billing",
        ClinicalDocumentType.COMMUNICATION_MESSAGE: "Message",
    }
    return labels.get(doc_type, doc_type.value)


class DocumentBase(BaseModel):
    """Base document model with common fields"""

    fileName: Optional[str] = None
    fileSize: Optional[int] = None
    fileUrl: Optional[str] = None
    interactionId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    mimeType: Optional[str] = None
    patientId: str = Field(..., min_length=1)
    summary: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    type: ClinicalDocumentType


class DocumentCreate(DocumentBase):
    """Model for creating a new document"""

    pass


class DocumentUpdate(BaseModel):
    """Model for updating an existing document (all fields optional)"""

    type: Optional[ClinicalDocumentType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = None
    interactionId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    """Model for document response with metadata"""

    id: str
    typeLabel: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    createdBy: str
    updatedBy: Optional[str] = None

    class Config:
        from_attributes = True
