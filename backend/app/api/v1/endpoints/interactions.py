"""Patient interaction endpoints - API route handlers"""

from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from typing import Optional

from app.models.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    NoteUpdateRequest,
)
from app.services.interaction_service import InteractionService
from app.dependencies import get_interaction_service

router = APIRouter(prefix="/interactions")


@router.get("/", response_model=list[InteractionResponse])
async def list_interactions(
    patientId: Optional[str] = Query(None, description="Filter by patient ID"),
    service: InteractionService = Depends(get_interaction_service),
):
    """Get all interactions, optionally filtered by patient ID"""
    if patientId:
        return await service.get_by_patient_id(patientId)
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

    # Validate interaction exists
    interaction = await service.get_by_id(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    # Read audio file
    audio_content = await audio.read()

    # Upload to object storage
    storage = await get_storage()
    storage_key = f"audio/{interaction_id}/{uuid4()}_{audio.filename}"

    try:
        storage_url = await storage.upload(
            key=storage_key,
            data=audio_content,
            content_type=audio.content_type or "audio/webm",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")

    # Store audio reference in interaction metadata
    existing_metadata = interaction.metadata or {}
    updated = await service.update(
        interaction_id,
        InteractionUpdate(
            metadata={
                **existing_metadata,
                "audio": {
                    "filename": audio.filename,
                    "storageKey": storage_key,
                    "storageUrl": storage_url,
                    "size": len(audio_content),
                    "contentType": audio.content_type,
                },
            }
        ),
    )

    # Mock transcription with background task
    async def mock_transcription():
        await asyncio.sleep(3)  # Simulate processing delay
        mock_transcript = "Mock transcript: Patient reported symptoms discussed during appointment."
        current_note = interaction.note or ""
        updated_note = f"{current_note}\n\n[Audio Transcript]\n{mock_transcript}".strip()
        await service.update_note(interaction_id, NoteUpdateRequest(note=updated_note))

    # Run in background (fire and forget)
    asyncio.create_task(mock_transcription())

    return {
        "interactionId": interaction_id,
        "filename": audio.filename,
        "storageKey": storage_key,
        "storageUrl": storage_url,
        "size": len(audio_content),
        "status": "stored",
        "message": "Audio uploaded to storage. Transcription will be processed asynchronously.",
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
