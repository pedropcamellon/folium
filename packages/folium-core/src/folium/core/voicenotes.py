"""Stable backend-to-voicenotes worker transport contracts."""

from folium.core.activities import TRANSCRIBE_ACTIVITY_NAME
from folium.core.models.workflow import (
    VOICENOTES_TASK_QUEUE,
    VOICENOTES_WORKFLOW_NAME,
    AudioReference,
    VoiceNotesInput,
)

__all__ = [
    "TRANSCRIBE_ACTIVITY_NAME",
    "VOICENOTES_TASK_QUEUE",
    "VOICENOTES_WORKFLOW_NAME",
    "AudioReference",
    "VoiceNotesInput",
]