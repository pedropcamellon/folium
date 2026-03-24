"""Patient data models (Pydantic)"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PatientBase(BaseModel):
    """Base patient model with common fields"""

    medical_record_number: str = Field(
        ..., min_length=1, max_length=50, alias="medicalRecordNumber"
    )
    first_name: str = Field(..., min_length=1, max_length=100, alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=100, alias="lastName")
    date_of_birth: date = Field(..., alias="dateOfBirth")
    gender: str = Field(..., min_length=1, max_length=20)
    contact_info: str = Field(..., min_length=1, max_length=200, alias="contactInfo")
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = Field(None, alias="emergencyContact")

    model_config = ConfigDict(populate_by_name=True)


class PatientCreate(PatientBase):
    """Model for creating a new patient"""

    pass


class PatientUpdate(BaseModel):
    """Model for updating an existing patient (all fields optional)"""

    model_config = ConfigDict(populate_by_name=True)

    medical_record_number: str | None = Field(
        None, min_length=1, max_length=50, alias="medicalRecordNumber"
    )
    first_name: str | None = Field(None, min_length=1, max_length=100, alias="firstName")
    last_name: str | None = Field(None, min_length=1, max_length=100, alias="lastName")
    date_of_birth: date | None = Field(None, alias="dateOfBirth")
    gender: str | None = Field(None, min_length=1, max_length=20)
    contact_info: str | None = Field(None, min_length=1, max_length=200, alias="contactInfo")
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = Field(None, alias="emergencyContact")


class PatientResponse(PatientBase):
    """Model for patient response with metadata"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
