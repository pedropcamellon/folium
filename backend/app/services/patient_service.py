"""Patient service - Business logic layer"""

from app.models.patient import PatientCreate, PatientUpdate, PatientResponse
from app.repositories.patient_repository import PatientRepository
from app.core.exceptions import PatientNotFoundError


class PatientService:
    """Business logic for patient operations"""

    def __init__(self, repository: PatientRepository):
        self.repository = repository

    async def get_all(self) -> list[PatientResponse]:
        """Get all patients"""
        patients = await self.repository.get_all()
        return [PatientResponse.model_validate(p) for p in patients]

    async def get_by_id(self, patient_id: str) -> PatientResponse:
        """Get patient by ID"""
        patient = await self.repository.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundError(patient_id)
        return PatientResponse.model_validate(patient)

    async def create(self, patient_data: PatientCreate) -> PatientResponse:
        """Create new patient"""
        # Could add business logic here (e.g., duplicate checking)
        patient_dict = patient_data.model_dump()

        patient = await self.repository.create(patient_dict)
        await self.repository.session.commit()

        return PatientResponse.model_validate(patient)

    async def update(self, patient_id: str, patient_data: PatientUpdate) -> PatientResponse:
        """Update patient"""
        # Verify patient exists
        existing = await self.repository.get_by_id(patient_id)
        if not existing:
            raise PatientNotFoundError(patient_id)

        # Get only fields that were provided
        update_dict = patient_data.model_dump(exclude_unset=True)

        updated = await self.repository.update(patient_id, update_dict)
        await self.repository.session.commit()
        return PatientResponse.model_validate(updated)

    async def delete(self, patient_id: str) -> bool:
        """Delete patient"""
        # Verify patient exists
        existing = await self.repository.get_by_id(patient_id)
        if not existing:
            raise PatientNotFoundError(patient_id)

        result = await self.repository.delete(patient_id)
        await self.repository.session.commit()
        return result
