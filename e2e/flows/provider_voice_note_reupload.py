from __future__ import annotations

import wave
from io import BytesIO
from typing import Any

import boto3
from botocore.exceptions import ClientError
from flow_cases import FlowCase
from patient_payloads import build_provider_test_patient
from playwright.sync_api import Page
from settings import (
    API_BASE_URL,
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
)
from ui import (
    create_encounter,
    create_patient,
    delete_patient,
    open_patient_history,
    patient_row,
)
from ui.session import log_step


def run_provider_voice_note_reupload_flow(
    page: Page, base_url: str, flow: FlowCase
) -> None:
    patient = build_provider_test_patient()
    encounter_title = f"Voice Note Re-upload {patient.medical_record_number}"
    storage_client = _storage_client()

    create_patient(page, flow, patient)
    try:
        open_patient_history(page, flow, patient)
        encounter_id = create_encounter(page, flow, encounter_title)
        first_upload = _upload_audio(page, encounter_id, _silent_wav())
        first_storage_key = _storage_key(page, encounter_id)
        assert first_storage_key == first_upload["storageKey"]
        storage_client.head_object(Bucket=MINIO_BUCKET, Key=first_storage_key)

        second_upload = _upload_audio(page, encounter_id, _silent_wav())
        second_storage_key = _storage_key(page, encounter_id)
        assert second_storage_key == second_upload["storageKey"]
        assert second_storage_key != first_storage_key
        storage_client.head_object(Bucket=MINIO_BUCKET, Key=second_storage_key)
        _assert_missing_object(storage_client, first_storage_key)
        log_step(
            flow.name, "Verified replacement audio exists and prior audio was deleted"
        )
    finally:
        page.goto(f"{base_url}{flow.expected_path}", wait_until="domcontentloaded")
        patient_row(page, patient).wait_for(state="visible", timeout=20000)
        delete_patient(page, flow, patient)


def _upload_audio(page: Page, encounter_id: str, content: bytes) -> dict[str, str]:
    log_step("provider", "Uploading synthetic voice-note audio")
    response = page.context.request.post(
        f"{API_BASE_URL}/api/v1/encounters/{encounter_id}/audio",
        headers=_api_headers(page),
        multipart={
            "audio": {
                "name": "voice-note.wav",
                "mimeType": "audio/wav",
                "buffer": content,
            }
        },
    )
    if not response.ok:
        raise AssertionError(
            f"Audio upload failed ({response.status}): {response.text()}"
        )
    payload = response.json()
    if not isinstance(payload, dict):
        raise TypeError("Audio upload did not return an object")
    storage_key = payload.get("storageKey")
    if not isinstance(storage_key, str):
        raise TypeError("Audio upload response did not include storageKey")
    return {"storageKey": storage_key}


def _storage_key(page: Page, encounter_id: str) -> str:
    response = page.context.request.get(
        f"{API_BASE_URL}/api/v1/encounters/{encounter_id}",
        headers=_api_headers(page),
    )
    if not response.ok:
        raise AssertionError(
            f"Encounter fetch failed ({response.status}): {response.text()}"
        )
    payload = response.json()
    if not isinstance(payload, dict):
        raise TypeError("Encounter fetch did not return an object")
    audio_metadata = payload.get("audioMetadata")
    if not isinstance(audio_metadata, dict):
        raise TypeError("Encounter did not include audio metadata")
    storage_key = audio_metadata.get("storageKey")
    if not isinstance(storage_key, str):
        raise TypeError("Encounter audio metadata did not include storageKey")
    return storage_key


def _api_headers(page: Page) -> dict[str, str]:
    token = page.evaluate("localStorage.getItem('auth_token')")
    if not isinstance(token, str):
        raise TypeError("Provider login did not create an authentication token")
    return {"Authorization": f"Bearer {token}"}


def _silent_wav() -> bytes:
    with BytesIO() as audio_buffer:
        with wave.open(audio_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16_000)
            wav_file.writeframes(b"\x00\x00" * 16_000)
        return audio_buffer.getvalue()


def _storage_client() -> Any:
    if not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
        raise RuntimeError(
            "Set FOLIUM_MINIO_ACCESS_KEY and FOLIUM_MINIO_SECRET_KEY to run "
            "provider-voice-note-reupload."
        )
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )


def _assert_missing_object(storage_client: Any, storage_key: str) -> None:
    try:
        storage_client.head_object(Bucket=MINIO_BUCKET, Key=storage_key)
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code in {"404", "NoSuchKey", "NotFound"}:
            return
        raise
    raise AssertionError(f"Previous audio object still exists: {storage_key}")
