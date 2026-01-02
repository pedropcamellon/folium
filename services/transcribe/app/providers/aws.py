"""AWS Transcribe provider (requires BAA for HIPAA)"""

import uuid
import time
import httpx
from typing import Optional
from .base import TranscriptionProvider
from app.config import settings


class AWSTranscribeProvider(TranscriptionProvider):
    """
    AWS Transcribe managed service.

    Requirements:
    - AWS Business Associate Agreement (BAA) for HIPAA
    - IAM user with AmazonTranscribeFullAccess
    - Temporary S3 bucket for non-S3 audio sources
    """

    def __init__(self):
        self.transcribe_client = None
        self.s3_client = None

    async def initialize(self) -> None:
        """Initialize AWS clients"""
        try:
            import boto3

            self.transcribe_client = boto3.client(
                "transcribe",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            self.s3_client = boto3.client(
                "s3",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            print(f"✅ AWS Transcribe initialized (region: {settings.AWS_REGION})")
        except ImportError:
            raise RuntimeError("boto3 not installed. Run: uv pip install -e .[aws]")

    async def transcribe(
        self,
        audio_url: str,
        language_code: str = "en-US",
        speaker_labels: bool = False,
        vocabulary_name: Optional[str] = None,
    ) -> dict:
        """Transcribe audio using AWS Transcribe"""
        start_time = time.time()

        # Determine if we need S3 bridge
        if audio_url.startswith("s3://") or "s3.amazonaws.com" in audio_url:
            media_uri = audio_url  # Direct S3 access
        else:
            # Download and upload to temp S3 bucket (for MinIO/Azure)
            media_uri = await self._bridge_to_s3(audio_url)

        # Submit transcription job
        job_name = f"transcribe-{uuid.uuid4()}"

        job_params = {
            "TranscriptionJobName": job_name,
            "Media": {"MediaFileUri": media_uri},
            "MediaFormat": "webm",  # Adjust based on actual format
            "LanguageCode": language_code,
        }

        # Add optional parameters
        if speaker_labels or vocabulary_name:
            job_params["Settings"] = {}
            if speaker_labels:
                job_params["Settings"]["ShowSpeakerLabels"] = True
                job_params["Settings"]["MaxSpeakerLabels"] = 10
            if vocabulary_name:
                job_params["Settings"]["VocabularyName"] = vocabulary_name

        self.transcribe_client.start_transcription_job(**job_params)

        # Poll for completion
        result = await self._poll_job(job_name)

        processing_time = time.time() - start_time
        result["processing_time"] = processing_time

        return result

    async def _bridge_to_s3(self, source_url: str) -> str:
        """Download from any provider, upload to temp S3 bucket"""
        # Download from source storage
        async with httpx.AsyncClient() as client:
            response = await client.get(source_url, timeout=60.0)
            response.raise_for_status()
            audio_data = response.content

        # Upload to temporary S3 bucket
        temp_key = f"temp/{uuid.uuid4()}.webm"
        self.s3_client.put_object(
            Bucket=settings.TEMP_S3_BUCKET,
            Key=temp_key,
            Body=audio_data,
            ServerSideEncryption="AES256",
        )

        # Return S3 URI
        return f"s3://{settings.TEMP_S3_BUCKET}/{temp_key}"

    async def _poll_job(self, job_name: str) -> dict:
        """Poll transcription job until complete"""
        import asyncio

        while True:
            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )

            status = response["TranscriptionJob"]["TranscriptionJobStatus"]

            if status == "COMPLETED":
                # Download transcript from S3
                transcript_uri = response["TranscriptionJob"]["Transcript"][
                    "TranscriptFileUri"
                ]

                async with httpx.AsyncClient() as client:
                    transcript_response = await client.get(transcript_uri)
                    transcript_data = transcript_response.json()

                # Parse AWS Transcribe response
                transcript = transcript_data["results"]["transcripts"][0]["transcript"]

                # Extract segments with speaker labels
                segments = []
                for item in transcript_data["results"]["items"]:
                    if item["type"] == "pronunciation":
                        segments.append(
                            {
                                "start_time": float(item["start_time"]),
                                "end_time": float(item["end_time"]),
                                "text": item["alternatives"][0]["content"],
                                "confidence": float(
                                    item["alternatives"][0]["confidence"]
                                ),
                                "speaker_label": item.get("speaker_label"),
                            }
                        )

                return {
                    "transcript": transcript,
                    "language_code": response["TranscriptionJob"]["LanguageCode"],
                    "confidence": None,  # AWS doesn't provide overall confidence
                    "segments": segments,
                    "job_id": job_name,
                    "processing_time": 0.0,  # Will be set by caller
                }

            elif status == "FAILED":
                failure_reason = response["TranscriptionJob"].get(
                    "FailureReason", "Unknown"
                )
                raise RuntimeError(f"AWS Transcribe job failed: {failure_reason}")

            # Wait before polling again
            await asyncio.sleep(2)

    def get_provider_name(self) -> str:
        return f"aws-transcribe-{settings.AWS_REGION}"
