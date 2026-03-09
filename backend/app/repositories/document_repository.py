"""Clinical document repository - Data access layer"""

import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db import Document
from app.models.document import ClinicalDocumentType, get_type_label

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Database-backed document repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[dict]:
        """Get all documents"""
        result = await self.session.execute(
            select(Document).options(selectinload(Document.patient))
        )
        documents = result.scalars().all()
        return [self._to_dict(doc) for doc in documents]

    async def get_by_id(self, id: str) -> dict | None:
        """Get document by ID"""
        try:
            document_id = UUID(id)
        except ValueError:
            return

        result = await self.session.execute(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.patient))
        )
        document = result.scalar_one_or_none()
        return self._to_dict(document) if document else None

    async def get_by_patient_id(
        self, patient_id: str, types: list[str] | None = None
    ) -> list[dict]:
        """Get all documents for a specific patient, optionally filtered by type"""
        try:
            patient_uuid = UUID(patient_id)
        except ValueError:
            return []

        query = select(Document).where(Document.patient_id == patient_uuid)

        if types:
            query = query.where(Document.type.in_(types))

        result = await self.session.execute(query.options(selectinload(Document.patient)))
        documents = result.scalars().all()
        return [self._to_dict(doc) for doc in documents]

    async def get_by_interaction_id(self, interaction_id: str) -> list[dict]:
        """Get all documents linked to a specific interaction"""
        try:
            interaction_uuid = UUID(interaction_id)
        except ValueError:
            return []

        result = await self.session.execute(
            select(Document)
            .where(Document.interaction_id == interaction_uuid)
            .options(selectinload(Document.patient))
        )
        documents = result.scalars().all()
        return [self._to_dict(doc) for doc in documents]

    async def create(self, document_data: dict) -> dict:
        """Create new document"""
        db_data = self._to_db_fields(document_data)
        document = Document(**db_data)
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return self._to_dict(document)

    async def update(self, id: str, document_data: dict) -> dict | None:
        """Update existing document"""
        try:
            document_id = UUID(id)
        except ValueError:
            logger.warning(f"Invalid document ID format: {id}")
            return

        result = await self.session.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        if not document:
            return

        # Update fields
        db_data = self._to_db_fields(document_data)
        for key, value in db_data.items():
            if value is not None and hasattr(document, key):
                setattr(document, key, value)

        document.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(document)
        return self._to_dict(document)

    async def delete(self, id: str) -> bool:
        """Delete document"""
        try:
            document_id = UUID(id)
        except ValueError:
            return False

        result = await self.session.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()

        if document:
            await self.session.delete(document)
            await self.session.flush()
            return True
        return False

    def _to_dict(self, document: Document) -> dict:
        """Convert Document model to dict with camelCase fields"""
        # Generate type label
        try:
            doc_type = ClinicalDocumentType(document.type)
            type_label = get_type_label(doc_type)
        except ValueError:
            type_label = document.type

        return {
            "id": str(document.id),
            "patientId": str(document.patient_id),
            "interactionId": str(document.interaction_id) if document.interaction_id else None,
            "title": document.title,
            "type": document.type,
            "typeLabel": type_label,
            "fileName": document.file_name,
            "fileSize": document.file_size,
            "fileUrl": document.file_url,
            "mimeType": document.mime_type,
            "summary": document.summary,
            "metadata": document.metadata_json,
            "createdBy": document.created_by,
            "updatedBy": document.updated_by,
            "createdAt": document.created_at.isoformat() if document.created_at else None,
            "updatedAt": document.updated_at.isoformat() if document.updated_at else None,
        }

    def _to_db_fields(self, data: dict) -> dict:
        """Convert camelCase dict to snake_case for database model"""
        field_mapping = {
            "patientId": "patient_id",
            "interactionId": "interaction_id",
            "fileName": "file_name",
            "fileSize": "file_size",
            "fileUrl": "file_url",
            "mimeType": "mime_type",
            "createdBy": "created_by",
            "updatedBy": "updated_by",
            "metadata": "metadata_json",
        }

        db_data = {}
        for key, value in data.items():
            db_key = field_mapping.get(key, key)
            if value is not None:
                # Convert UUID strings to UUID objects for foreign keys
                if db_key in ("patient_id", "interaction_id") and isinstance(value, str):
                    try:
                        db_data[db_key] = UUID(value)
                    except ValueError:
                        pass
                else:
                    db_data[db_key] = value

        return db_data
