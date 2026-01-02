"""Pydantic models for API requests and responses"""

from pydantic import BaseModel, Field
from typing import Optional, List


class TranscriptionRequest(BaseModel):
    """Request model for transcription endpoint"""

    audio_url: str = Field(
        ..., description="Presigned URL to audio file (any storage provider)"
    )
    language_code: str = Field(
        default="en-US", description="Language code (e.g., en-US, es-ES)"
    )
    speaker_labels: bool = Field(
        default=False, description="Enable speaker diarization (AWS/Azure only)"
    )
    vocabulary_name: Optional[str] = Field(
        default=None, description="Custom medical vocabulary (AWS/Azure)"
    )


class TranscriptionSegment(BaseModel):
    """Segment of transcribed audio with timing"""

    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None
    speaker_label: Optional[str] = None


class TranscriptionResponse(BaseModel):
    """Response model for successful transcription"""

    transcript: str = Field(..., description="Full transcript text")
    language_code: str
    confidence: Optional[float] = Field(
        default=None, description="Overall confidence score (0-1)"
    )
    segments: List[TranscriptionSegment] = Field(default_factory=list)
    job_id: Optional[str] = None
    processing_time: float = Field(..., description="Processing time in seconds")


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str
    detail: Optional[str] = None
    job_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    provider: str
    model: Optional[str] = None
