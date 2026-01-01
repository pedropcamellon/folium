"""Clinical document service - Business logic layer"""

from typing import List, Optional
from app.models.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.repositories.document_repository import DocumentRepository
from app.core.exceptions import DocumentNotFoundError


class DocumentService:
    """Business logic for clinical document operations"""

    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    async def get_all(self) -> List[DocumentResponse]:
        """Get all documents"""
        documents = await self.repository.get_all()
        return [DocumentResponse(**d) for d in documents]

    async def get_by_id(self, document_id: str) -> DocumentResponse:
        """Get document by ID"""
        document = await self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(document_id)
        return DocumentResponse(**document)

    async def get_by_patient_id(
        self, patient_id: str, types: Optional[List[str]] = None
    ) -> List[DocumentResponse]:
        """Get all documents for a specific patient, optionally filtered by type"""
        documents = await self.repository.get_by_patient_id(patient_id, types)
        # Sort by creation date descending (most recent first)
        sorted_documents = sorted(documents, key=lambda x: x.get("createdAt", ""), reverse=True)
        return [DocumentResponse(**d) for d in sorted_documents]

    async def get_by_interaction_id(self, interaction_id: str) -> List[DocumentResponse]:
        """Get all documents linked to a specific interaction"""
        documents = await self.repository.get_by_interaction_id(interaction_id)
        return [DocumentResponse(**d) for d in documents]

    async def create(self, document_data: DocumentCreate) -> DocumentResponse:
        """Create new document"""
        document_dict = document_data.model_dump()

        # Convert enum to string value
        if document_dict.get("type"):
            document_dict["type"] = document_dict["type"].value

        document = await self.repository.create(document_dict)
        return DocumentResponse(**document)

    async def update(self, document_id: str, document_data: DocumentUpdate) -> DocumentResponse:
        """Update document"""
        # Verify document exists
        existing = await self.repository.get_by_id(document_id)
        if not existing:
            raise DocumentNotFoundError(document_id)

        # Get only fields that were provided
        update_dict = document_data.model_dump(exclude_unset=True)

        # Convert enum to string value if present
        if update_dict.get("type"):
            update_dict["type"] = update_dict["type"].value

        updated = await self.repository.update(document_id, update_dict)
        return DocumentResponse(**updated)

    async def delete(self, document_id: str) -> bool:
        """Delete document"""
        existing = await self.repository.get_by_id(document_id)
        if not existing:
            raise DocumentNotFoundError(document_id)

        return await self.repository.delete(document_id)
