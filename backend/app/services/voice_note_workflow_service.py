"""Temporal client wrapper for voice note workflows."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from dataclasses import asdict, is_dataclass
from datetime import timedelta

from uuid import uuid4

from temporalio.client import Client, WorkflowExecutionStatus, WorkflowFailureError

from app.config import settings


@dataclass
class AudioReference:
    storage_key: str
    audio_url: str
    original_filename: str | None = None
    content_type: str | None = None


@dataclass
class VoiceNoteWorkflowInput:
    interaction_id: str
    patient_id: str
    audio: AudioReference


class VoiceNoteWorkflowService:
    """Starts and inspects Temporal workflows for voice notes."""

    def __init__(self) -> None:
        self._client: Client | None = None
        self._client_lock = asyncio.Lock()

    async def _get_client(self) -> Client:
        if self._client is not None:
            return self._client

        async with self._client_lock:
            if self._client is None:
                self._client = await Client.connect(
                    settings.TEMPORAL_ADDRESS,
                    namespace=settings.TEMPORAL_NAMESPACE,
                )

        return self._client

    def build_workflow_id(self, interaction_id: str) -> str:
        return f"voice-note-{interaction_id}-{uuid4().hex[:8]}"

    async def start_voice_note_workflow(
        self,
        interaction_id: str,
        patient_id: str,
        storage_key: str,
        audio_url: str,
        original_filename: str | None,
        content_type: str | None,
    ) -> dict[str, str]:
        client = await self._get_client()
        workflow_input = VoiceNoteWorkflowInput(
            interaction_id=interaction_id,
            patient_id=patient_id,
            audio=AudioReference(
                storage_key=storage_key,
                audio_url=audio_url,
                original_filename=original_filename,
                content_type=content_type,
            ),
        )
        workflow_id = self.build_workflow_id(interaction_id)
        handle = await client.start_workflow(
            settings.VOICE_NOTE_WORKFLOW_NAME,
            workflow_input,
            id=workflow_id,
            task_queue=settings.VOICE_NOTE_TASK_QUEUE,
            execution_timeout=timedelta(
                minutes=settings.VOICE_NOTE_WORKFLOW_EXECUTION_TIMEOUT_MINUTES
            ),
        )

        return {
            "workflowId": handle.id,
            "runId": handle.result_run_id or handle.first_execution_run_id or handle.run_id or "",
        }

    async def get_voice_note_workflow_state(
        self,
        workflow_id: str,
        run_id: str | None = None,
    ) -> dict:
        client = await self._get_client()
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)
        description = await handle.describe()
        result: dict | None = None
        error_message: str | None = None

        if description.status == WorkflowExecutionStatus.COMPLETED:
            workflow_result = await handle.result()
            if is_dataclass(workflow_result):
                result = asdict(workflow_result)
                status_value = result.get("status")
                if status_value is not None:
                    result["status"] = getattr(status_value, "value", status_value)
            else:
                result = workflow_result if isinstance(workflow_result, dict) else {"value": workflow_result}
        elif description.status in {
            WorkflowExecutionStatus.FAILED,
            WorkflowExecutionStatus.CANCELED,
            WorkflowExecutionStatus.TERMINATED,
            WorkflowExecutionStatus.TIMED_OUT,
        }:
            try:
                await handle.result()
            except WorkflowFailureError as exc:
                error_message = str(exc.cause or exc)

        return {
            "workflowId": description.id,
            "runId": description.run_id,
            "status": description.status.name.lower(),
            "result": result,
            "errorMessage": error_message,
        }
