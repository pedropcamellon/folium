"""Patient repository - Database access layer"""

from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.patient import Patient


class PatientRepository:
    """Patient repository using PostgreSQL via SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[dict]:
        """Get all patients"""
        result = await self.session.execute(select(Patient))
        patients = result.scalars().all()
        return [self._to_dict(patient) for patient in patients]

    async def get_by_id(self, patient_id: str) -> Optional[dict]:
        """Get patient by ID"""
        try:
            patient_uuid = UUID(patient_id)
        except (ValueError, AttributeError):
            return

        result = await self.session.execute(select(Patient).where(Patient.id == patient_uuid))
        patient = result.scalar_one_or_none()
        return self._to_dict(patient) if patient else None

    async def create(self, patient_data: dict) -> dict:
        """Create new patient"""
        # Convert camelCase to snake_case for database
        db_data = self._to_db_fields(patient_data)

        patient = Patient(**db_data)
        self.session.add(patient)
        await self.session.flush()
        await self.session.refresh(patient)

        return self._to_dict(patient)

    async def update(self, patient_id: str, patient_data: dict) -> Optional[dict]:
        """Update existing patient"""
        try:
            patient_uuid = UUID(patient_id)
        except (ValueError, AttributeError):
            return

        result = await self.session.execute(select(Patient).where(Patient.id == patient_uuid))
        patient = result.scalar_one_or_none()

        if not patient:
            return

        # Convert camelCase to snake_case and update fields
        db_data = self._to_db_fields(patient_data)
        for key, value in db_data.items():
            if value is not None and hasattr(patient, key):
                setattr(patient, key, value)

        patient.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(patient)

        return self._to_dict(patient)

    async def delete(self, patient_id: str) -> bool:
        """Delete patient (cascade deletes interactions and documents)"""
        try:
            patient_uuid = UUID(patient_id)
        except (ValueError, AttributeError):
            return False

        result = await self.session.execute(select(Patient).where(Patient.id == patient_uuid))
        patient = result.scalar_one_or_none()

        if patient:
            await self.session.delete(patient)
            await self.session.flush()
            return True
        return False

    def _to_dict(self, patient: Patient) -> dict:
        """Convert Patient model to API dict (snake_case -> camelCase)"""
        return {
            "id": str(patient.id),
            "medicalRecordNumber": patient.medical_record_number,
            "firstName": patient.first_name,
            "lastName": patient.last_name,
            "dateOfBirth": patient.date_of_birth.isoformat(),
            "gender": patient.gender,
            "contactInfo": patient.contact_info,
            "email": patient.email,
            "phone": patient.phone,
            "address": patient.address,
            "emergencyContact": patient.emergency_contact,
            "createdAt": patient.created_at.isoformat(),
            "updatedAt": patient.updated_at.isoformat() if patient.updated_at else None,
        }

    def _to_db_fields(self, api_data: dict) -> dict:
        """Convert API data (camelCase) to database fields (snake_case)"""
        field_mapping = {
            "medicalRecordNumber": "medical_record_number",
            "firstName": "first_name",
            "lastName": "last_name",
            "dateOfBirth": "date_of_birth",
            "contactInfo": "contact_info",
            "emergencyContact": "emergency_contact",
        }

        db_data = {}
        for api_key, value in api_data.items():
            db_key = field_mapping.get(api_key, api_key)
            db_data[db_key] = value

        return db_data
