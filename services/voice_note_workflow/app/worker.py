import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from app.activities.voice_note_activities import VoiceNoteActivities
from app.clients.transcription_client import TranscriptionServiceClient
from app.config import settings
from app.workflows.voice_note_workflow import VoiceNoteWorkflow


async def main() -> None:
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    client = await Client.connect(
        settings.TEMPORAL_ADDRESS,
        namespace=settings.TEMPORAL_NAMESPACE,
    )

    activities = VoiceNoteActivities(
        transcription_gateway=TranscriptionServiceClient(
            settings.TRANSCRIPTION_SERVICE_URL,
            settings.REQUEST_TIMEOUT_SECONDS,
        ),
    )

    worker = Worker(
        client,
        task_queue=settings.VOICE_NOTE_TASK_QUEUE,
        workflows=[VoiceNoteWorkflow],
        activities=[
            activities.transcribe_audio,
        ],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())