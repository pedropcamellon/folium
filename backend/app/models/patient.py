"""Patient data models (Pydantic)"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date


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
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, alias="emergencyContact")

    model_config = ConfigDict(populate_by_name=True)


class PatientCreate(PatientBase):
    """Model for creating a new patient"""

    pass


class PatientUpdate(BaseModel):
    """Model for updating an existing patient (all fields optional)"""

    model_config = ConfigDict(populate_by_name=True)

    medical_record_number: Optional[str] = Field(
        None, min_length=1, max_length=50, alias="medicalRecordNumber"
    )
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="firstName")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="lastName")
    date_of_birth: Optional[date] = Field(None, alias="dateOfBirth")
    gender: Optional[str] = Field(None, min_length=1, max_length=20)
    contact_info: Optional[str] = Field(None, min_length=1, max_length=200, alias="contactInfo")
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, alias="emergencyContact")


class PatientResponse(PatientBase):
    """Model for patient response with metadata"""

    id: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True  # Enable ORM mode for future DB models
