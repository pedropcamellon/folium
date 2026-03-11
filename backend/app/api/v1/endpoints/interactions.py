"""Patient interaction endpoints - API route handlers"""

from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from typing import Optional

from app.models.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    NoteUpdateRequest,
    SummaryUpdateRequest,
)
from app.services.interaction_service import InteractionService
from app.dependencies import get_interaction_service

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interactions")


@router.get("/", response_model=list[InteractionResponse])
async def list_interactions(
    patientId: Optional[str] = Query(None, description="Filter by patient ID"),
    service: InteractionService = Depends(get_interaction_service),
):
    """Get all interactions, optionally filtered by patient ID"""
    logger.info(f"[API] list_interactions called with patientId={patientId}")
    if patientId:
        logger.info(f"[API] Calling service.get_by_patient_id({patientId})")
        result = await service.get_by_patient_id(patientId)
        logger.info(f"[API] Service returned {len(result)} interactions")
        return result
    logger.info("[API] No patientId filter, calling get_all")
    return await service.get_all()


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: str, service: InteractionService = Depends(get_interaction_service)
):
    """Get interaction by ID"""
    return await service.get_by_id(interaction_id)


@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction: InteractionCreate, service: InteractionService = Depends(get_interaction_service)
):
    """Create new interaction"""
    return await service.create(interaction)


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: str,
    interaction: InteractionUpdate,
    service: InteractionService = Depends(get_interaction_service),
):
    """Update existing interaction"""
    return await service.update(interaction_id, interaction)


@router.patch("/{interaction_id}/note", response_model=InteractionResponse)
async def update_interaction_note(
    interaction_id: str,
    note_data: NoteUpdateRequest,
    service: InteractionService = Depends(get_interaction_service),
):
    """Update just the note field of an interaction"""
    return await service.update_note(interaction_id, note_data)


@router.patch("/{interaction_id}/summary", response_model=InteractionResponse)
async def update_interaction_summary(
    interaction_id: str,
    summary_data: SummaryUpdateRequest,
    service: InteractionService = Depends(get_interaction_service),
):
    """Update just the summary field of an interaction"""
    return await service.update_summary(interaction_id, summary_data)


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: str, service: InteractionService = Depends(get_interaction_service)
):
    """Delete interaction"""
    await service.delete(interaction_id)


@router.post("/{interaction_id}/audio", response_model=dict)
async def upload_audio(
    interaction_id: str,
    audio: UploadFile = File(...),
    service: InteractionService = Depends(get_interaction_service),
):
    """Upload audio file to object storage and trigger transcription"""
    from fastapi import HTTPException
    from app.services.storage import get_storage
    from uuid import uuid4
    import asyncio

    logger.info(f"🎙️ [UPLOAD] POST /audio called for {interaction_id}")

    # Validate interaction exists
    interaction = await service.get_by_id(interaction_id)
    if not interaction:
        logger.info(f"❌ [UPLOAD] Interaction {interaction_id} not found")
        raise HTTPException(status_code=404, detail="Interaction not found")

    logger.info(f"✅ [UPLOAD] Interaction found: {interaction.id}")

    # Read audio file
    audio_content = await audio.read()
    logger.info(f"📁 [UPLOAD] Read {len(audio_content)} bytes from {audio.filename}")

    # Upload to object storage
    storage = await get_storage()
    storage_key = f"audio/{interaction_id}/{uuid4()}_{audio.filename}"
    logger.info(f"🔑 [UPLOAD] Generated storage key: {storage_key}")

    try:
        storage_url = await storage.upload(
            key=storage_key,
            data=audio_content,
            content_type=audio.content_type or "audio/webm",
        )
        logger.info(f"☁️ [UPLOAD] Uploaded to storage: {storage_url}")
    except Exception as e:
        logger.info(f"❌ [UPLOAD] Storage upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")

    # Store audio reference in interaction metadata
    existing_metadata = interaction.metadata or {}
    audio_metadata = {
        "filename": audio.filename,
        "storageKey": storage_key,
        "storageUrl": storage_url,
        "size": len(audio_content),
        "contentType": audio.content_type,
    }
    logger.info(f"📦 [UPLOAD] Audio metadata to save: {audio_metadata}")

    updated = await service.update(
        interaction_id,
        InteractionUpdate(
            metadata={
                **existing_metadata,
                "audio": audio_metadata,
            }
        ),
    )

    logger.info(f"💾 [UPLOAD] Database updated. Result metadata: {updated.metadata}")

    # Verify the save worked by re-fetching
    verify = await service.get_by_id(interaction_id)
    logger.info(f"🔍 [UPLOAD] Verification fetch: {verify.metadata}")

    # Start transcription in background (fire and forget)
    logger.info("🚀 [UPLOAD] Triggering background transcription task")
    asyncio.create_task(
        transcribe_audio(
            interaction_id=interaction_id,
            storage=storage,
            storage_key=storage_key,
            service=service,
            interaction=interaction,
            existing_metadata=existing_metadata,
        )
    )

    return {
        "interactionId": interaction_id,
        "filename": audio.filename,
        "storageKey": storage_key,
        "storageUrl": storage_url,
        "size": len(audio_content),
        "status": "stored",
        "message": "Audio uploaded to storage. Transcription in progress.",
    }


@router.get("/{interaction_id}/audio")
async def get_audio(
    interaction_id: str,
    service: InteractionService = Depends(get_interaction_service),
):
    """Download audio file from object storage"""
    from fastapi import HTTPException
    from fastapi.responses import Response
    from app.services.storage import get_storage

    interaction = await service.get_by_id(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    metadata = interaction.metadata or {}
    audio_data = metadata.get("audio")

    if not audio_data or not audio_data.get("storageKey"):
        raise HTTPException(status_code=404, detail="No audio found for this interaction")

    # Download from object storage
    storage = await get_storage()
    storage_key = audio_data["storageKey"]

    try:
        audio_bytes = await storage.download(storage_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage download failed: {str(e)}")

    return Response(
        content=audio_bytes,
        media_type=audio_data.get("contentType", "audio/webm"),
        headers={
            "Content-Disposition": f'inline; filename="{audio_data.get("filename", "audio.webm")}"'
        },
    )


# Trigger transcription with microservice
async def transcribe_audio(
    interaction_id: str,
    storage,
    storage_key: str,
    service: InteractionService,
    interaction,
    existing_metadata: dict,
):
    """Background task to transcribe audio"""
    from app.services.transcription_service import get_transcription_service

    logger.info(f"🚀 BACKGROUND TASK STARTED for {interaction_id}")  # Console output for debugging
    logger.info(f"🎤 Starting transcription for interaction {interaction_id}")

    try:
        # Generate presigned URL for transcription service to access audio
        presigned_url = await storage.get_presigned_url(storage_key, expiration=3600)
        logger.info(f"🔗 Generated presigned URL: {presigned_url[:80]}...")

        # Call transcription microservice
        transcription_svc = get_transcription_service()
        logger.info(f"📞 Calling transcription service...")

        result = await transcription_svc.transcribe(
            audio_url=presigned_url, language_code="en-US", speaker_labels=False
        )

        logger.info(f"✅ Transcription service returned result: {result.keys()}")

        # Update interaction note with transcript
        transcript = result.get("transcript", "")
        logger.info(f"📝 Transcript received ({len(transcript)} chars): {transcript[:100]}...")

        if transcript and transcript.strip():
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Overwrite note with new transcript
            updated_note = f"{transcript}\n{timestamp}".strip()

            logger.info(f"💾 Updating interaction note (length: {len(updated_note)} chars)")
            await service.update_note(interaction_id, NoteUpdateRequest(note=updated_note))
        else:
            logger.info("⚠️ Transcript empty, skipping note update")

        logger.info(f"✅ Transcription completed for {interaction_id}")

    except Exception as e:
        logger.error(
            f"❌ Transcription failed for interaction {interaction_id}: {e}", exc_info=True
        )

        # Optionally update interaction with error status
        await service.update(
            interaction_id,
            InteractionUpdate(
                metadata={
                    **existing_metadata,
                    "audio": {
                        **existing_metadata.get("audio", {}),
                        "transcriptionError": str(e),
                        "transcriptionStatus": "failed",
                    },
                }
            ),
        )
