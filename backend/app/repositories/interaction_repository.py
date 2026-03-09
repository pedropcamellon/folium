"""Patient interaction repository - Database access layer"""

from datetime import datetime, timezone
from uuid import UUID
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db.interaction import Interaction

logger = logging.getLogger(__name__)


class InteractionRepository:
    """Interaction repository using PostgreSQL via SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[dict]:
        """Get all interactions"""
        result = await self.session.execute(
            select(Interaction).options(selectinload(Interaction.patient))
        )
        interactions = result.scalars().all()
        return [self._to_dict(interaction) for interaction in interactions]

    async def get_by_id(self, interaction_id: str) -> dict | None:
        """Get interaction by ID"""
        try:
            interaction_uuid = UUID(interaction_id)
        except (ValueError, AttributeError):
            return None

        result = await self.session.execute(
            select(Interaction)
            .where(Interaction.id == interaction_uuid)
            .options(selectinload(Interaction.patient))
        )
        interaction = result.scalar_one_or_none()
        return self._to_dict(interaction) if interaction else None

    async def get_by_patient_id(self, patient_id: str) -> list[dict]:
        """Get all interactions for a specific patient"""
        logger.info(f"[REPO] get_by_patient_id called with patient_id={patient_id}")
        try:
            patient_uuid = UUID(patient_id)
            logger.info(f"[REPO] Converted to UUID: {patient_uuid}")
        except (ValueError, AttributeError) as e:
            logger.error(f"[REPO] Invalid UUID: {e}")
            return []

        result = await self.session.execute(
            select(Interaction)
            .where(Interaction.patient_id == patient_uuid)
            .options(selectinload(Interaction.patient))
        )
        interactions = result.scalars().all()
        logger.info(f"[REPO] Found {len(interactions)} interactions")
        if interactions:
            logger.info(f"[REPO] First interaction: {interactions[0].id}")
        return [self._to_dict(interaction) for interaction in interactions]

    async def create(self, interaction_data: dict) -> dict:
        """Create new interaction"""
        db_data = self._to_db_fields(interaction_data)

        interaction = Interaction(**db_data)
        self.session.add(interaction)
        await self.session.flush()
        await self.session.refresh(interaction, ["patient"])

        return self._to_dict(interaction)

    async def update(self, interaction_id: str, interaction_data: dict) -> dict | None:
        """Update existing interaction"""
        try:
            interaction_uuid = UUID(interaction_id)
        except (ValueError, AttributeError):
            return None

        result = await self.session.execute(
            select(Interaction)
            .where(Interaction.id == interaction_uuid)
            .options(selectinload(Interaction.patient))
        )
        interaction = result.scalar_one_or_none()

        if not interaction:
            return None

        db_data = self._to_db_fields(interaction_data)
        for key, value in db_data.items():
            if value is not None and hasattr(interaction, key):
                setattr(interaction, key, value)

        interaction.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(interaction, ["patient"])

        return self._to_dict(interaction)

    async def delete(self, interaction_id: str) -> bool:
        """Delete interaction"""
        try:
            interaction_uuid = UUID(interaction_id)
        except (ValueError, AttributeError):
            return False

        result = await self.session.execute(
            select(Interaction).where(Interaction.id == interaction_uuid)
        )
        interaction = result.scalar_one_or_none()

        if interaction:
            await self.session.delete(interaction)
            await self.session.flush()
            return True
        return False

    def _to_dict(self, interaction: Interaction) -> dict:
        """Convert Interaction model to API dict (snake_case -> camelCase)"""
        return {
            "id": str(interaction.id),
            "patientId": str(interaction.patient_id),
            "type": interaction.type,
            "title": interaction.title,
            "description": interaction.description,
            "interactionDate": interaction.interaction_date.isoformat(),
            "location": interaction.location,
            "providerId": interaction.provider_id,
            "providerName": interaction.provider_name,
            "summary": interaction.summary,
            "note": interaction.note,
            "audioDocumentId": interaction.audio_document_id,
            "isCompliant": interaction.is_compliant,
            "metadata": interaction.metadata_json,
            "structuredSummary": interaction.structured_summary,
            "chiefComplaint": interaction.chief_complaint,
            "clinicalAssessment": interaction.clinical_assessment,
            "treatmentPlan": interaction.treatment_plan,
            "createdBy": interaction.created_by,
            "updatedBy": interaction.updated_by,
            "createdAt": interaction.created_at.isoformat(),
            "updatedAt": interaction.updated_at.isoformat() if interaction.updated_at else None,
        }

    def _to_db_fields(self, api_data: dict) -> dict:
        """Convert API data (camelCase) to database fields (snake_case)"""
        field_mapping = {
            "patientId": "patient_id",
            "interactionDate": "interaction_date",
            "providerId": "provider_id",
            "providerName": "provider_name",
            "audioDocumentId": "audio_document_id",
            "isCompliant": "is_compliant",
            "metadata": "metadata_json",
            "structuredSummary": "structured_summary",
            "chiefComplaint": "chief_complaint",
            "clinicalAssessment": "clinical_assessment",
            "treatmentPlan": "treatment_plan",
            "createdBy": "created_by",
            "updatedBy": "updated_by",
        }

        return {field_mapping.get(k, k): v for k, v in api_data.items()}
