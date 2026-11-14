"""Patient repository - Database access layer"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PatientNotFoundError
from app.models.db.patient import Patient

logger = logging.getLogger(__name__)


async def require_active_patient(session: AsyncSession, patient_id: UUID | str) -> UUID:
    """Return a patient UUID only when the patient exists and is active."""
    try:
        patient_uuid = UUID(str(patient_id))
    except (ValueError, TypeError, AttributeError) as error:
        raise PatientNotFoundError(str(patient_id)) from error

    active_patient_id = await session.scalar(
        select(Patient.id).where(
            Patient.id == patient_uuid,
            Patient.is_active.is_(True),
        )
    )
    if active_patient_id is None:
        raise PatientNotFoundError(str(patient_uuid))
    return patient_uuid


class PatientRepository:
    """Patient repository using PostgreSQL via SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Patient]:
        """Get all patients"""
        result = await self.session.execute(select(Patient).where(Patient.is_active.is_(True)))
        patients = result.scalars().all()
        return list(patients)

    async def get_by_id(self, patient_id: str) -> Patient | None:
        """Get patient by ID"""
        try:
            patient_uuid = UUID(patient_id)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid patient ID format: {patient_id}")
            return

        result = await self.session.execute(
            select(Patient).where(
                Patient.id == patient_uuid,
                Patient.is_active.is_(True),
            )
        )
        patient = result.scalar_one_or_none()
        return patient

    async def create(self, patient_data: dict) -> Patient:
        """Create new patient"""
        patient = Patient(**patient_data)
        self.session.add(patient)
        await self.session.flush()
        await self.session.refresh(patient)

        return patient

    async def update(self, patient_id: str, patient_data: dict) -> Patient | None:
        """Update existing patient"""
        try:
            patient_uuid = UUID(patient_id)
        except (ValueError, AttributeError):
            return

        result = await self.session.execute(
            select(Patient).where(
                Patient.id == patient_uuid,
                Patient.is_active.is_(True),
            )
        )
        patient = result.scalar_one_or_none()

        if not patient:
            logger.warning(f"Patient with ID {patient_id} not found for update")
            return

        # Defend against unwanted updates by only allowing specific fields to be updated
        allowed_fields = {
            "medical_record_number",
            "first_name",
            "last_name",
            "date_of_birth",
            "email",
            "phone",
            "address",
            "emergency_contact",
            "gender",
            "contact_info",
        }

        for key, value in patient_data.items():
            if key in allowed_fields:
                setattr(patient, key, value)

        patient.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(patient)

        return patient

    async def deactivate(self, patient_id: str) -> bool:
        """Deactivate a patient without deleting its clinical records."""
        try:
            patient_uuid = UUID(patient_id)
        except (ValueError, AttributeError):
            return False

        result = await self.session.execute(
            select(Patient).where(
                Patient.id == patient_uuid,
                Patient.is_active.is_(True),
            )
        )
        patient = result.scalar_one_or_none()

        if patient:
            patient.is_active = False
            patient.updated_at = datetime.now(UTC)
            await self.session.flush()
            return True
        return False
