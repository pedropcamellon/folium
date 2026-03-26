from temporalio import activity

from app.contracts.voice_note_models import AudioReference, TranscriptionResult
from app.contracts.workflow_protocols import TranscriptionGateway
from app.temporal_config import (
    TRANSCRIBE_ACTIVITY_NAME,
)


class VoiceNoteActivities:
    def __init__(
        self,
        transcription_gateway: TranscriptionGateway,
    ):
        self.transcription_gateway = transcription_gateway

    @activity.defn(name=TRANSCRIBE_ACTIVITY_NAME)
    async def transcribe_audio(self, audio: AudioReference) -> TranscriptionResult:
        if not audio.audio_url:
            raise ValueError(
                "Minimal worker implementation requires audio.audio_url. "
                "Later iterations can derive signed URLs from storage metadata."
            )
        return await self.transcription_gateway.transcribe(audio.audio_url)
