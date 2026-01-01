"""Dependency injection for FastAPI"""

from fastapi import Depends
from app.repositories.patient_repository import PatientRepository
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.document_repository import DocumentRepository
from app.services.patient_service import PatientService
from app.services.interaction_service import InteractionService
from app.services.document_service import DocumentService

# Repository singletons (in-memory for MVP)
_patient_repository = None
_interaction_repository = None
_document_repository = None


def get_patient_repository() -> PatientRepository:
    """Get or create patient repository instance"""
    global _patient_repository
    if _patient_repository is None:
        _patient_repository = PatientRepository()
    return _patient_repository


def get_patient_service(
    repository: PatientRepository = Depends(get_patient_repository),
) -> PatientService:
    """Get patient service with injected repository"""
    return PatientService(repository)


def get_interaction_repository() -> InteractionRepository:
    """Get or create interaction repository instance"""
    global _interaction_repository
    if _interaction_repository is None:
        _interaction_repository = InteractionRepository()
    return _interaction_repository


def get_interaction_service(
    repository: InteractionRepository = Depends(get_interaction_repository),
) -> InteractionService:
    """Get interaction service with injected repository"""
    return InteractionService(repository)


def get_document_repository() -> DocumentRepository:
    """Get or create document repository instance"""
    global _document_repository
    if _document_repository is None:
        _document_repository = DocumentRepository()
    return _document_repository


def get_document_service(
    repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentService:
    """Get document service with injected repository"""
    return DocumentService(repository)
