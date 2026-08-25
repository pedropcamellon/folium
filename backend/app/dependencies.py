"""Dependency injection for FastAPI"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.repositories.document_repository import DocumentRepository
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.patient_repository import PatientRepository
from app.services.document_service import DocumentService
from app.services.interaction_service import InteractionService
from app.services.patient_service import PatientService
from app.services.storage.base import ObjectStorageProvider
from app.services.storage.factory import get_storage
from app.services.summarization_service import SummarizationService
from app.services.transcription_service import TranscriptionService
from app.services.voice_note_service import VoiceNoteService
from app.services.voicenotes_service import VoiceNotesService

# Singletons (for services without database dependencies)
_transcription_service = None
_summarization_service = None
_voicenotes_service = None


def get_patient_repository(session: AsyncSession = Depends(get_async_session)) -> PatientRepository:
    """Get patient repository with database session"""
    return PatientRepository(session)


def get_patient_service(
    repository: PatientRepository = Depends(get_patient_repository),
) -> PatientService:
    """Get patient service with injected repository"""
    return PatientService(repository)


def get_interaction_repository(
    session: AsyncSession = Depends(get_async_session),
) -> InteractionRepository:
    """Get interaction repository with database session"""
    return InteractionRepository(session)


def get_interaction_service(
    repository: InteractionRepository = Depends(get_interaction_repository),
) -> InteractionService:
    """Get interaction service with injected repository"""
    return InteractionService(repository)


def get_document_repository(
    session: AsyncSession = Depends(get_async_session),
) -> DocumentRepository:
    """Get document repository with database session"""
    return DocumentRepository(session)


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


def get_voicenotes_service() -> VoiceNotesService:
    """Get voicenotes service instance (singleton)."""
    global _voicenotes_service
    if _voicenotes_service is None:
        _voicenotes_service = VoiceNotesService()
    return _voicenotes_service


async def get_storage_provider() -> ObjectStorageProvider:
    """Get storage provider instance (singleton)"""
    return await get_storage()


async def get_voice_note_service(
    interaction_service: InteractionService = Depends(get_interaction_service),
    workflow_service: VoiceNotesService = Depends(get_voicenotes_service),
    storage_provider: ObjectStorageProvider = Depends(get_storage_provider),
) -> VoiceNoteService:
    """Get voice note orchestration service with injected collaborators."""
    return VoiceNoteService(interaction_service, workflow_service, storage_provider)
