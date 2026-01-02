"""Dependency injection for FastAPI"""

from fastapi import Depends
from app.repositories.patient_repository import PatientRepository
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.document_repository import DocumentRepository
from app.services.patient_service import PatientService
from app.services.interaction_service import InteractionService
from app.services.document_service import DocumentService
from app.services.transcription_service import TranscriptionService
from app.services.summarization_service import SummarizationService

# Repository singletons (in-memory for MVP)
_patient_repository = None
_interaction_repository = None
_document_repository = None
_transcription_service = None
_summarization_service = None


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


def get_transcription_service() -> TranscriptionService:
    """Get transcription service instance (singleton)"""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service


def get_summarization_service() -> SummarizationService:
    """Get summarization service instance (singleton)"""
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service
