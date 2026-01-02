"""Azure Speech provider (requires BAA for HIPAA)"""

import httpx
import time
import tempfile
import os
from typing import Optional
from .base import TranscriptionProvider
from app.config import settings


class AzureSpeechProvider(TranscriptionProvider):
    """
    Azure Speech managed service.

    Requirements:
    - Azure Business Associate Agreement (BAA) for HIPAA
    - Azure Cognitive Services Speech resource
    """

    def __init__(self):
        self.speech_config = None

    async def initialize(self) -> None:
        """Initialize Azure Speech SDK"""
        try:
            import azure.cognitiveservices.speech as speechsdk

            self.speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION,
            )

            print(
                f"[OK] Azure Speech initialized (region: {settings.AZURE_SPEECH_REGION})"
            )
        except ImportError:
            raise RuntimeError(
                "azure-cognitiveservices-speech not installed. Run: uv pip install -e .[azure]"
            )

    async def transcribe(
        self,
        audio_url: str,
        language_code: str = "en-US",
        speaker_labels: bool = False,
        vocabulary_name: Optional[str] = None,
    ) -> dict:
        """Transcribe audio using Azure Speech"""
        import azure.cognitiveservices.speech as speechsdk

        start_time = time.time()

        # Download audio from presigned URL
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url, timeout=60.0)
            response.raise_for_status()
            audio_data = response.content

        # Save to temporary file (Azure SDK requires file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            # Configure speech recognition
            self.speech_config.speech_recognition_language = language_code
            audio_config = speechsdk.audio.AudioConfig(filename=temp_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, audio_config=audio_config
            )

            # Recognize speech
            result = recognizer.recognize_once()

            processing_time = time.time() - start_time

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "transcript": result.text,
                    "language_code": language_code,
                    "confidence": None,  # Azure doesn't provide confidence in batch mode
                    "segments": [],  # Azure doesn't provide segments in batch mode
                    "job_id": None,
                    "processing_time": processing_time,
                }
            elif result.reason == speechsdk.ResultReason.NoMatch:
                raise RuntimeError("No speech could be recognized")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                raise RuntimeError(
                    f"Speech recognition canceled: {cancellation.reason}"
                )
            else:
                raise RuntimeError(f"Unknown result reason: {result.reason}")

        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_provider_name(self) -> str:
        return f"azure-speech-{settings.AZURE_SPEECH_REGION}"
