from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VoiceNoteWorkflowStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    TRANSCRIBED = "transcribed"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AudioReference:
    storage_key: str
    audio_url: str | None = None
    bucket: str | None = None
    original_filename: str | None = None
    content_type: str | None = None


@dataclass
class VoiceNoteWorkflowInput:
    interaction_id: str
    patient_id: str
    audio: AudioReference


@dataclass
class TranscriptionResult:
    transcript: str
    language_code: str | None = None
    confidence: float | None = None
    processing_time: float | None = None
    provider: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SummaryResult:
    summary: str
    structured_summary: dict[str, Any] | None = None
    processing_time: float | None = None
    provider: str | None = None
    model_used: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceNoteWorkflowResult:
    interaction_id: str
    status: VoiceNoteWorkflowStatus
    transcript_saved: bool
    transcript: str | None = None
    failure_stage: str | None = None
    error_message: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "interaction_id": self.interaction_id,
            "status": self.status.value,
            "transcript": self.transcript,
            "transcript_saved": self.transcript_saved,
            "failure_stage": self.failure_stage,
            "error_message": self.error_message,
        }


def workflow_result_to_payload(result: VoiceNoteWorkflowResult) -> dict[str, Any]:
    return result.to_payload()