"""Voice note application service for upload, workflow orchestration, and status lookup."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.models.interaction import InteractionUpdate
from app.services.interaction_service import InteractionService
from app.services.storage.base import ObjectStorageProvider
from app.services.voicenotes_service import VoiceNotesService


class VoiceNoteService:
    """Coordinates object storage, interaction updates, and Temporal workflow state."""

    def __init__(
        self,
        interaction_service: InteractionService,
        workflow_service: VoiceNotesService,
        storage_provider: ObjectStorageProvider,
    ) -> None:
        self.interaction_service = interaction_service
        self.workflow_service = workflow_service
        self.storage_provider = storage_provider

    async def upload_audio(
        self,
        interaction_id: str,
        filename: str | None,
        content_type: str | None,
        audio_content: bytes,
    ) -> dict:
        interaction = await self.interaction_service.get_by_id(interaction_id)
        storage_key = f"audio/{interaction_id}/{uuid4()}_{filename}"
        storage_url = await self.storage_provider.upload(
            key=storage_key,
            data=audio_content,
            content_type=content_type or "audio/webm",
        )

        audio_metadata = {
            "filename": filename,
            "storageKey": storage_key,
            "storageUrl": storage_url,
            "size": len(audio_content),
            "contentType": content_type,
        }

        await self.interaction_service.update(
            interaction_id,
            InteractionUpdate(
                metadata={
                    **(interaction.metadata or {}),
                    "audio": audio_metadata,
                }
            ),
        )

        workflow_execution = await self.start_workflow(interaction_id)
        return {
            "interactionId": interaction_id,
            "filename": filename,
            "storageKey": storage_key,
            "storageUrl": storage_url,
            "size": len(audio_content),
            "status": "processing",
            "workflowId": workflow_execution["workflowId"],
            "runId": workflow_execution["runId"],
            "message": "Audio uploaded. Voice note workflow started.",
        }

    async def get_audio_download(self, interaction_id: str) -> dict:
        interaction = await self.interaction_service.get_by_id(interaction_id)
        audio_data = (interaction.metadata or {}).get("audio") or {}
        storage_key = audio_data.get("storageKey")

        if not storage_key:
            raise ValueError("No audio found for this interaction")

        audio_bytes = await self.storage_provider.download(storage_key)
        return {
            "content": audio_bytes,
            "mediaType": audio_data.get("contentType", "audio/webm"),
            "filename": audio_data.get("filename", "audio.webm"),
        }

    async def start_workflow(self, interaction_id: str) -> dict[str, str]:
        interaction = await self.interaction_service.get_by_id(interaction_id)
        metadata = interaction.metadata or {}
        audio_data = dict(metadata.get("audio") or {})
        storage_key = audio_data.get("storageKey")

        if not storage_key:
            raise ValueError("No audio uploaded for this interaction")

        presigned_url = await self.storage_provider.get_presigned_url(
            storage_key,
            expiration=3600,
            internal=True,
        )

        workflow_execution = await self.workflow_service.start_voicenotes(
            interaction_id=interaction_id,
            patient_id=interaction.patientId,
            storage_key=storage_key,
            audio_url=presigned_url,
            original_filename=audio_data.get("filename"),
            content_type=audio_data.get("contentType"),
        )

        audio_data["transcriptionStatus"] = "processing"
        audio_data["voiceNoteWorkflow"] = {
            **workflow_execution,
            "status": "processing",
            "updatedAt": self._now_iso(),
        }

        await self.interaction_service.update_fields(
            interaction_id,
            {
                "metadata": {
                    **metadata,
                    "audio": audio_data,
                }
            },
        )
        return workflow_execution

    async def get_workflow_status(self, interaction_id: str) -> dict:
        interaction = await self.interaction_service.get_by_id(interaction_id)
        metadata = interaction.metadata or {}
        audio_data = metadata.get("audio") or {}
        workflow_metadata = audio_data.get("voiceNoteWorkflow") or {}
        workflow_id = workflow_metadata.get("workflowId")
        run_id = workflow_metadata.get("runId")

        if not workflow_id:
            return {
                "interactionId": interaction_id,
                "status": "idle",
                "interaction": interaction.model_dump(),
            }

        workflow_state = await self.workflow_service.get_voicenotes_state(workflow_id, run_id)
        temporal_status = workflow_state["status"]
        status_value = "processing"
        error_message = workflow_state.get("errorMessage")

        if temporal_status == "completed":
            result = workflow_state.get("result") or {}
            status_value = result.get("status", "completed")
            interaction = await self._apply_workflow_result(interaction_id, workflow_state)
        elif temporal_status in {"failed", "canceled", "terminated", "timed_out"}:
            status_value = "failed"
            interaction = await self._mark_workflow_failed(
                interaction_id,
                metadata,
                audio_data,
                workflow_metadata,
                error_message,
            )

        return {
            "interactionId": interaction_id,
            "workflowId": workflow_id,
            "runId": run_id,
            "status": status_value,
            "failureStage": workflow_metadata.get("failureStage")
            or (workflow_state.get("result") or {}).get("failure_stage"),
            "errorMessage": error_message or workflow_metadata.get("errorMessage"),
            "interaction": interaction.model_dump(),
        }

    async def _apply_workflow_result(self, interaction_id: str, workflow_state: dict):
        interaction = await self.interaction_service.get_by_id(interaction_id)
        metadata = interaction.metadata or {}
        audio_data = dict(metadata.get("audio") or {})
        workflow_metadata = dict(audio_data.get("voiceNoteWorkflow") or {})

        if workflow_metadata.get("transcriptAppliedAt"):
            return interaction

        result = workflow_state.get("result") or {}
        result_status = result.get("status", "completed")
        transcript = result.get("transcript")
        error_message = result.get("error_message") or workflow_state.get("errorMessage")

        workflow_metadata.update(
            {
                "workflowId": workflow_state.get("workflowId"),
                "runId": workflow_state.get("runId"),
                "status": result_status,
                "failureStage": result.get("failure_stage"),
                "errorMessage": error_message,
                "updatedAt": self._now_iso(),
                "transcriptAppliedAt": self._now_iso(),
            }
        )
        audio_data["voiceNoteWorkflow"] = workflow_metadata
        audio_data["transcriptionStatus"] = result_status

        update_data = {
            "metadata": {
                **metadata,
                "audio": audio_data,
            }
        }

        if transcript:
            update_data["note"] = transcript

        return await self.interaction_service.update_fields(interaction_id, update_data)

    async def _mark_workflow_failed(
        self,
        interaction_id: str,
        metadata: dict,
        audio_data: dict,
        workflow_metadata: dict,
        error_message: str | None,
    ):
        updated_audio_data = dict(audio_data)
        updated_workflow_metadata = dict(workflow_metadata)
        updated_workflow_metadata.update(
            {
                "status": "failed",
                "errorMessage": error_message,
                "updatedAt": self._now_iso(),
            }
        )
        updated_audio_data["voiceNoteWorkflow"] = updated_workflow_metadata
        updated_audio_data["transcriptionStatus"] = "failed"
        return await self.interaction_service.update_fields(
            interaction_id,
            {
                "metadata": {
                    **metadata,
                    "audio": updated_audio_data,
                }
            },
        )

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(UTC).isoformat()
