"""Patient interaction data models (Pydantic)"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class InteractionType(str, Enum):
    """Types of patient interactions"""

    APPOINTMENT = "Appointment"
    VACCINATION = "Vaccination"
    MEDICATION = "Medication"
    LAB_WORK = "LabWork"
    PROCEDURE = "Procedure"
    VOICE_NOTE = "VoiceNote"
    IMAGING = "Imaging"
    SURGERY = "Surgery"
    CONSULTATION = "Consultation"
    EMERGENCY = "Emergency"
    DISCHARGE = "Discharge"
    ADMISSION = "Admission"


class InteractionBase(BaseModel):
    """Base interaction model with common fields"""

    patientId: str = Field(..., min_length=1)
    type: InteractionType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    interactionDate: datetime
    location: Optional[str] = None
    providerId: Optional[str] = None
    providerName: Optional[str] = None
    summary: Optional[str] = None
    note: Optional[str] = None
    audioDocumentId: Optional[str] = None
    isCompliant: bool = True
    metadata: Optional[Dict[str, Any]] = None

    # Clinical summary fields (from summarization service)
    structured_summary: Optional[Dict[str, Any]] = None  # Full SOAP note
    chief_complaint: Optional[str] = None
    clinical_assessment: Optional[str] = None
    treatment_plan: Optional[str] = None


class InteractionCreate(InteractionBase):
    """Model for creating a new interaction"""

    pass


class InteractionUpdate(BaseModel):
    """Model for updating an existing interaction (all fields optional)"""

    type: Optional[InteractionType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    interactionDate: Optional[datetime] = None
    location: Optional[str] = None
    providerId: Optional[str] = None
    providerName: Optional[str] = None
    summary: Optional[str] = None
    note: Optional[str] = None
    audioDocumentId: Optional[str] = None
    isCompliant: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class NoteUpdateRequest(BaseModel):
    """Model for updating just the note field"""

    note: str


class InteractionResponse(InteractionBase):
    """Model for interaction response with metadata"""

    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    createdBy: str
    updatedBy: Optional[str] = None

    class Config:
        from_attributes = True
