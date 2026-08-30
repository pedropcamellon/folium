"""Patient interaction endpoints - API route handlers"""

from secrets import compare_digest

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from folium.core.chart_review import ChartReviewHistoryRequest, ChartReviewHistoryResponse

from app.config import settings
from app.core.logging import AuditLogger, setup_structured_logging
from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.dependencies import (
    get_chart_review_request_service,
    get_interaction_service,
    get_voice_note_service,
)
from app.models.chart_review import ChartReviewResponse
from app.models.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionUpdate,
    NoteUpdateRequest,
    SummaryUpdateRequest,
)
from app.models.user import User
from app.services.chart_review_request_service import ChartReviewRequestService
from app.services.interaction_service import InteractionService
from app.services.voice_note_service import VoiceNoteService

logger: AuditLogger = setup_structured_logging("backend")

router = APIRouter(prefix="/interactions")


@router.get("/", response_model=list[InteractionResponse])
async def list_interactions(
    patientId: str | None = Query(None, description="Filter by patient ID"),
    current_user: User = Depends(require_permission(Permission.INTERACTIONS_READ)),
    service: InteractionService = Depends(get_interaction_service),
):
    """Get all interactions, optionally filtered by patient ID"""
    logger.info(f"[API] list_interactions called with patientId={patientId}")
    logger.audit(
        action="interactions_list_accessed",
        user_id=str(current_user.id),
        patient_id=patientId if patientId else None,
        method="GET",
        endpoint="/api/v1/interactions",
    )
    if patientId:
        logger.info(f"[API] Calling service.get_by_patient_id({patientId})")
        result = await service.get_by_patient_id(patientId)
        logger.info(f"[API] Service returned {len(result)} interactions")
        return result
    logger.info("[API] No patientId filter, calling get_all")
    return await service.get_all()


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: str,
    current_user: User = Depends(require_permission(Permission.INTERACTIONS_READ)),
    service: InteractionService = Depends(get_interaction_service),
):
    """Get interaction by ID"""
    interaction = await service.get_by_id(interaction_id)
    logger.audit(
        action="interaction_accessed",
        user_id=str(current_user.id),
        patient_id=str(interaction.patientId),
        interaction_id=interaction_id,
        method="GET",
        endpoint=f"/api/v1/interactions/{interaction_id}",
    )
    return interaction


@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction: InteractionCreate,
    current_user: User = Depends(require_permission(Permission.INTERACTIONS_CREATE)),
    service: InteractionService = Depends(get_interaction_service),
):
    """Create new interaction"""
    result = await service.create(interaction)
    logger.audit(
        action="interaction_created",
        user_id=str(current_user.id),
        patient_id=str(result.patientId),
        interaction_id=str(result.id),
        method="POST",
        endpoint="/api/v1/interactions",
    )
    return result


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: str,
    interaction: InteractionUpdate,
    _: object = Depends(require_permission(Permission.INTERACTIONS_UPDATE)),
    service: InteractionService = Depends(get_interaction_service),
):
    """Update existing interaction"""
    return await service.update(interaction_id, interaction)


@router.patch("/{interaction_id}/note", response_model=InteractionResponse)
async def update_interaction_note(
    interaction_id: str,
    note_data: NoteUpdateRequest,
    current_user: User = Depends(require_permission(Permission.INTERACTIONS_UPDATE)),
    service: InteractionService = Depends(get_interaction_service),
):
    """Update just the note field of an interaction"""
    result = await service.update_note(interaction_id, note_data)
    logger.audit(
        action="interaction_note_updated",
        user_id=str(current_user.id),
        patient_id=str(result.patientId),
        interaction_id=interaction_id,
        method="PATCH",
        endpoint=f"/api/v1/interactions/{interaction_id}/note",
    )
    return result


@router.patch("/{interaction_id}/summary", response_model=InteractionResponse)
async def update_interaction_summary(
    interaction_id: str,
    summary_data: SummaryUpdateRequest,
    _: object = Depends(require_permission(Permission.INTERACTIONS_SUMMARIZE)),
    service: InteractionService = Depends(get_interaction_service),
):
    """Update just the summary field of an interaction"""
    return await service.update_summary(interaction_id, summary_data)


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: str,
    current_user: User = Depends(require_permission(Permission.INTERACTIONS_DELETE)),
    service: InteractionService = Depends(get_interaction_service),
):
    """Delete interaction"""
    interaction = await service.get_by_id(interaction_id)
    logger.audit(
        action="interaction_deleted",
        user_id=str(current_user.id),
        patient_id=str(interaction.patientId),
        interaction_id=interaction_id,
        method="DELETE",
        endpoint=f"/api/v1/interactions/{interaction_id}",
    )
    await service.delete(interaction_id)


@router.post("/{interaction_id}/audio", response_model=dict)
async def upload_audio(
    interaction_id: str,
    audio: UploadFile = File(...),
    current_user: User = Depends(require_permission(Permission.VOICE_RECORD)),
    voice_note_service: VoiceNoteService = Depends(get_voice_note_service),
    interaction_service: InteractionService = Depends(get_interaction_service),
):
    """Upload audio file to object storage and start the voice note workflow."""
    logger.info(f"[UPLOAD] POST /audio called for {interaction_id}")

    # Get interaction to log patient_id
    interaction = await interaction_service.get_by_id(interaction_id)

    audio_content = await audio.read()
    logger.info(f"[UPLOAD] Read {len(audio_content)} bytes from {audio.filename}")

    logger.audit(
        action="voice_note_uploaded",
        user_id=str(current_user.id),
        patient_id=str(interaction.patientId),
        interaction_id=interaction_id,
        audio_filename=audio.filename,
        file_size=len(audio_content),
        method="POST",
        endpoint=f"/api/v1/interactions/{interaction_id}/audio",
    )

    try:
        return await voice_note_service.upload_audio(
            interaction_id=interaction_id,
            filename=audio.filename,
            content_type=audio.content_type,
            audio_content=audio_content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"[UPLOAD] Voice note upload failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{interaction_id}/audio")
async def get_audio(
    interaction_id: str,
    current_user: User = Depends(require_permission(Permission.VOICE_REVIEW)),
    voice_note_service: VoiceNoteService = Depends(get_voice_note_service),
    interaction_service: InteractionService = Depends(get_interaction_service),
):
    """Download audio file from object storage"""
    logger.info(f"[GET] GET /audio called for {interaction_id}")

    # Get interaction to log patient_id
    interaction = await interaction_service.get_by_id(interaction_id)

    logger.audit(
        action="voice_note_accessed",
        user_id=str(current_user.id),
        patient_id=str(interaction.patientId),
        interaction_id=interaction_id,
        method="GET",
        endpoint=f"/api/v1/interactions/{interaction_id}/audio",
    )

    try:
        audio_download = await voice_note_service.get_audio_download(interaction_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"[GET] Download failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Storage download failed: {exc!s}") from exc

    return Response(
        content=audio_download["content"],
        media_type=audio_download["mediaType"],
        headers={"Content-Disposition": f'inline; filename="{audio_download["filename"]}"'},
    )


@router.post("/{interaction_id}/transcribe", response_model=dict)
async def trigger_transcription(
    interaction_id: str,
    _: object = Depends(require_permission(Permission.VOICE_REVIEW)),
    voice_note_service: VoiceNoteService = Depends(get_voice_note_service),
):
    """Start the voice note workflow for existing audio."""
    logger.info(f"[TRANSCRIBE] POST /transcribe called for {interaction_id}")

    try:
        workflow_execution = await voice_note_service.start_workflow(interaction_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "interactionId": interaction_id,
        "status": "processing",
        "workflowId": workflow_execution["workflowId"],
        "runId": workflow_execution["runId"],
        "message": "Voice note workflow started.",
    }


@router.get("/{interaction_id}/voice-note-status", response_model=dict)
async def get_voice_note_status(
    interaction_id: str,
    _: object = Depends(require_permission(Permission.INTERACTIONS_READ)),
    voice_note_service: VoiceNoteService = Depends(get_voice_note_service),
):
    """Get current voice note workflow status for an interaction."""
    return await voice_note_service.get_workflow_status(interaction_id)


@router.post("/{interaction_id}/chart-review", response_model=ChartReviewResponse)
async def request_chart_review(
    interaction_id: str,
    current_user: User = Depends(require_permission(Permission.INTERACTIONS_SUMMARIZE)),
    service: ChartReviewRequestService = Depends(get_chart_review_request_service),
):
    """Generate an explicitly requested, mock-backed draft chart review."""
    result = await service.request_for_interaction(interaction_id)
    logger.audit(
        action="chart_review_requested",
        user_id=str(current_user.id),
        interaction_id=interaction_id,
        method="POST",
        endpoint=f"/api/v1/interactions/{interaction_id}/chart-review",
    )
    return result


@router.get("/{interaction_id}/chart-review", response_model=ChartReviewResponse | None)
async def get_chart_review(
    interaction_id: str,
    _: object = Depends(require_permission(Permission.INTERACTIONS_READ)),
    service: ChartReviewRequestService = Depends(get_chart_review_request_service),
):
    """Read the latest persisted draft review for an interaction."""
    return await service.get_for_interaction(interaction_id)


@router.post("/internal/chart-review/history", response_model=ChartReviewHistoryResponse)
async def retrieve_chart_review_history(
    request: ChartReviewHistoryRequest,
    internal_token: str = Header(..., alias="X-ChartReview-Internal-Token"),
    service: ChartReviewRequestService = Depends(get_chart_review_request_service),
):
    """Serve the worker's bounded, backend-curated prior-interaction blocks."""
    if not compare_digest(internal_token, settings.CHARTREVIEW_INTERNAL_TOKEN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal token")
    try:
        return await service.retrieve_prior_interaction_blocks(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
