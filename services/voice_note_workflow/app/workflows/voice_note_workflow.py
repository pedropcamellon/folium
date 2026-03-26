from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

from app.contracts.voice_note_models import (
    TranscriptionResult,
    VoiceNoteWorkflowInput,
    VoiceNoteWorkflowResult,
    VoiceNoteWorkflowStatus,
)
from app.temporal_config import (
    TRANSCRIBE_ACTIVITY_NAME,
    VOICE_NOTE_WORKFLOW_NAME,
)


@workflow.defn(name=VOICE_NOTE_WORKFLOW_NAME)
class VoiceNoteWorkflow:
    @workflow.run
    async def run(self, input_data: VoiceNoteWorkflowInput) -> VoiceNoteWorkflowResult:
        retry_policy = RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0)

        try:
            transcript_result = await workflow.execute_activity(
                TRANSCRIBE_ACTIVITY_NAME,
                args=[input_data.audio],
                result_type=TranscriptionResult,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy,
            )
        except Exception as exc:
            workflow.logger.error("Voice note transcription stage failed: %s", exc)
            raise ApplicationError(
                f"Voice note transcription failed: {exc}",
                type="transcription",
            )

        return VoiceNoteWorkflowResult(
            interaction_id=input_data.interaction_id,
            status=VoiceNoteWorkflowStatus.COMPLETED,
            transcript_saved=True,
            transcript=transcript_result.transcript,
        )
