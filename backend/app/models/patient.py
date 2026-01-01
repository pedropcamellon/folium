"""Patient data models (Pydantic)"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PatientBase(BaseModel):
    """Base patient model with common fields"""
    medicalRecordNumber: str = Field(..., min_length=1, max_length=50)
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    dateOfBirth: datetime
    gender: str = Field(..., min_length=1, max_length=20)
    contactInfo: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergencyContact: Optional[str] = None


class PatientCreate(PatientBase):
    """Model for creating a new patient"""
    pass


class PatientUpdate(BaseModel):
    """Model for updating an existing patient (all fields optional)"""
    medicalRecordNumber: Optional[str] = Field(None, min_length=1, max_length=50)
    firstName: Optional[str] = Field(None, min_length=1, max_length=100)
    lastName: Optional[str] = Field(None, min_length=1, max_length=100)
    dateOfBirth: Optional[datetime] = None
    gender: Optional[str] = Field(None, min_length=1, max_length=20)
    contactInfo: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergencyContact: Optional[str] = None


class PatientResponse(PatientBase):
    """Model for patient response with metadata"""
    id: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Enable ORM mode for future DB models
