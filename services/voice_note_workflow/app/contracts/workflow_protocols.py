from typing import Protocol

from app.contracts.voice_note_models import TranscriptionResult


class TranscriptionGateway(Protocol):
    async def transcribe(self, audio_url: str) -> TranscriptionResult: ...