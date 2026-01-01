"""Patient service - Business logic layer"""

from typing import List, Optional
from app.models.patient import PatientCreate, PatientUpdate, PatientResponse
from app.repositories.patient_repository import PatientRepository
from app.core.exceptions import PatientNotFoundError


class PatientService:
    """Business logic for patient operations"""
    
    def __init__(self, repository: PatientRepository):
        self.repository = repository
    
    async def get_all(self) -> List[PatientResponse]:
        """Get all patients"""
        patients = await self.repository.get_all()
        return [PatientResponse(**p) for p in patients]
    
    async def get_by_id(self, patient_id: str) -> PatientResponse:
        """Get patient by ID"""
        patient = await self.repository.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundError(patient_id)
        return PatientResponse(**patient)
    
    async def create(self, patient_data: PatientCreate) -> PatientResponse:
        """Create new patient"""
        # Could add business logic here (e.g., duplicate checking)
        patient_dict = patient_data.model_dump()
        # Convert datetime to ISO string for storage
        if patient_dict.get("dateOfBirth"):
            patient_dict["dateOfBirth"] = patient_dict["dateOfBirth"].isoformat()
        
        patient = await self.repository.create(patient_dict)
        return PatientResponse(**patient)
    
    async def update(self, patient_id: str, patient_data: PatientUpdate) -> PatientResponse:
        """Update patient"""
        # Verify patient exists
        existing = await self.repository.get_by_id(patient_id)
        if not existing:
            raise PatientNotFoundError(patient_id)
        
        # Get only fields that were provided
        update_dict = patient_data.model_dump(exclude_unset=True)
        # Convert datetime to ISO string if present
        if update_dict.get("dateOfBirth"):
            update_dict["dateOfBirth"] = update_dict["dateOfBirth"].isoformat()
        
        updated = await self.repository.update(patient_id, update_dict)
        return PatientResponse(**updated)
    
    async def delete(self, patient_id: str) -> bool:
        """Delete patient"""
        # Verify patient exists
        existing = await self.repository.get_by_id(patient_id)
        if not existing:
            raise PatientNotFoundError(patient_id)
        
        return await self.repository.delete(patient_id)
