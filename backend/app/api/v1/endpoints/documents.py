"""Clinical document endpoints - API route handlers"""

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import RedirectResponse

from app.core.logging import setup_structured_logging
from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.dependencies import get_document_service, get_storage_provider
from app.models.document import (
    ClinicalDocumentType,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.storage.base import ObjectStorageProvider

router = APIRouter(prefix="/clinical-documents")
logger = setup_structured_logging("backend")


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    patientId: str | None = Query(None, description="Filter by patient ID"),
    types: str | None = Query(None, description="Comma-separated document types to filter"),
    interactionId: str | None = Query(None, description="Filter by interaction ID"),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ)),
    service: DocumentService = Depends(get_document_service),
):
    """Get all documents with optional filters"""
    logger.audit(
        action="documents_list_accessed",
        user_id=str(current_user.id),
        patient_id=patientId if patientId else None,
        interaction_id=interactionId if interactionId else None,
        method="GET",
        endpoint="/api/v1/clinical-documents",
    )

    if interactionId:
        return await service.get_by_interaction_id(interactionId)

    if patientId:
        type_list = types.split(",") if types else None
        return await service.get_by_patient_id(patientId, type_list)

    return await service.get_all()


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ)),
    service: DocumentService = Depends(get_document_service),
):
    """Get document by ID"""
    document = await service.get_by_id(document_id)
    logger.audit(
        action="document_accessed",
        user_id=str(current_user.id),
        patient_id=str(document.patientId),
        document_id=document_id,
        document_type=document.type,
        method="GET",
        endpoint=f"/api/v1/clinical-documents/{document_id}",
    )
    return document


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_CREATE)),
    service: DocumentService = Depends(get_document_service),
):
    """Create new document"""
    result = await service.create(document)
    logger.audit(
        action="document_created",
        user_id=str(current_user.id),
        patient_id=str(result.patientId),
        document_id=str(result.id),
        document_type=result.type,
        method="POST",
        endpoint="/api/v1/clinical-documents",
    )
    return result


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document: DocumentUpdate,
    _: object = Depends(require_permission(Permission.DOCUMENTS_UPDATE)),
    service: DocumentService = Depends(get_document_service),
):
    """Update existing document"""
    return await service.update(document_id, document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_DELETE)),
    service: DocumentService = Depends(get_document_service),
):
    """Delete document"""
    document = await service.get_by_id(document_id)
    logger.audit(
        action="document_deleted",
        user_id=str(current_user.id),
        patient_id=str(document.patientId),
        document_id=document_id,
        document_type=document.type,
        method="DELETE",
        endpoint=f"/api/v1/clinical-documents/{document_id}",
    )
    await service.delete(document_id)


# File validation constants
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".txt", ".docx", ".doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MIME_TYPE_MAP = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".txt": "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
}


def validate_file(file: UploadFile) -> tuple[str, str]:
    """Validate file type and size, return extension and mime type"""
    # Get file extension
    file_ext = Path(file.filename or "").suffix.lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Get MIME type
    mime_type = MIME_TYPE_MAP.get(file_ext, "application/octet-stream")

    return file_ext, mime_type


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for storage"""
    # Remove path components
    name = Path(filename).name
    # Replace spaces and special chars
    name = name.replace(" ", "_")
    # Keep only alphanumeric, underscore, hyphen, dot
    name = "".join(c for c in name if c.isalnum() or c in "._-")
    return name


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    patientId: str = Form(...),
    type: ClinicalDocumentType = Form(...),
    title: str = Form(...),
    summary: str | None = Form(None),
    interactionId: str | None = Form(None),
    _: object = Depends(require_permission(Permission.DOCUMENTS_CREATE)),
    storage: ObjectStorageProvider = Depends(get_storage_provider),
    service: DocumentService = Depends(get_document_service),
):
    """Upload document file with metadata"""
    logger.info(f"[UPLOAD] Starting upload for patient {patientId}, type {type}")

    # Validate file
    file_ext, mime_type = validate_file(file)

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate storage key
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    sanitized_name = sanitize_filename(file.filename or "document")
    storage_key = f"documents/{patientId}/{timestamp}_{unique_id}_{sanitized_name}"

    # Upload to storage
    logger.info(f"[UPLOAD] Uploading to storage: {storage_key}")
    file_url = await storage.upload(
        key=storage_key,
        data=file_content,
        content_type=mime_type,
        metadata={
            "patient_id": patientId,
            "document_type": type.value,
            "original_filename": file.filename or "",
        },
    )

    # Create document record
    document_data = DocumentCreate(
        patientId=patientId,
        type=type,
        title=title,
        summary=summary,
        interactionId=interactionId,
        fileUrl=file_url,
        fileName=file.filename,
        fileSize=file_size,
        mimeType=mime_type,
    )

    result = await service.create(document_data)
    logger.info(f"[UPLOAD] Document created: {result.id}")

    return result


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    _: object = Depends(require_permission(Permission.DOCUMENTS_READ)),
    storage: ObjectStorageProvider = Depends(get_storage_provider),
    service: DocumentService = Depends(get_document_service),
):
    """Download document file"""
    # Get document metadata
    document = await service.get_by_id(document_id)

    if not document.fileUrl:
        raise HTTPException(status_code=404, detail="Document has no file attached")

    # Extract storage key from fileUrl
    # Format: http://endpoint/bucket/documents/patient-id/filename
    # We need: documents/patient-id/filename (exclude bucket name)
    storage_key = "/".join(document.fileUrl.split("/")[-3:])  # Last 3 parts (no bucket)

    logger.info(f"[VIEW] Extracted storage_key: {storage_key} from fileUrl: {document.fileUrl}")

    # Generate presigned URL
    presigned_url = await storage.get_presigned_url(storage_key, expiration=3600)

    logger.info(f"[DOWNLOAD] Generated presigned URL for document {document_id}")

    # Redirect to presigned URL
    return RedirectResponse(url=presigned_url)


@router.get("/{document_id}/view")
async def view_document(
    document_id: str,
    _: object = Depends(require_permission(Permission.DOCUMENTS_READ)),
    storage: ObjectStorageProvider = Depends(get_storage_provider),
    service: DocumentService = Depends(get_document_service),
):
    """View document inline (for preview)"""
    # Same as download but with inline disposition
    # For now, just redirect to presigned URL (browser will handle inline display)
    return await download_document(document_id, storage, service)
