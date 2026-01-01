"""Clinical document endpoints - API route handlers"""

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.models.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services.document_service import DocumentService
from app.dependencies import get_document_service

router = APIRouter(prefix="/clinical-documents")


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    patientId: Optional[str] = Query(None, description="Filter by patient ID"),
    types: Optional[str] = Query(None, description="Comma-separated document types to filter"),
    interactionId: Optional[str] = Query(None, description="Filter by interaction ID"),
    service: DocumentService = Depends(get_document_service)
):
    """Get all documents with optional filters"""
    if interactionId:
        return await service.get_by_interaction_id(interactionId)
    
    if patientId:
        type_list = types.split(",") if types else None
        return await service.get_by_patient_id(patientId, type_list)
    
    return await service.get_all()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID"""
    return await service.get_by_id(document_id)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Create new document"""
    return await service.create(document)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document: DocumentUpdate,
    service: DocumentService = Depends(get_document_service)
):
    """Update existing document"""
    return await service.update(document_id, document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Delete document"""
    await service.delete(document_id)
