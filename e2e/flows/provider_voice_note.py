from __future__ import annotations

from playwright.sync_api import Page

from flow_cases import FlowCase
from patient_payloads import build_provider_test_patient

from mocks import install_interaction_mocks, remove_interaction_mocks
from ui import (
    create_interaction,
    create_patient,
    delete_patient,
    open_interaction_details,
    open_patient_history,
    patient_row,
    record_and_submit_audio,
)


def run_provider_voice_note_flow(
    page: Page, base_url: str, flow: FlowCase, transcript: str
) -> None:
    patient = build_provider_test_patient()
    interaction_title = f"Voice Note {patient.medical_record_number}"

    create_patient(page, flow, patient)
    try:
        open_patient_history(page, flow, patient)
        interaction_id = create_interaction(page, flow, interaction_title)
        routes = install_interaction_mocks(page, interaction_id, transcript)
        try:
            open_interaction_details(page, flow, interaction_title)
            record_and_submit_audio(page, flow, transcript)
        finally:
            remove_interaction_mocks(page, routes)
    finally:
        page.goto(f"{base_url}{flow.expected_path}", wait_until="domcontentloaded")
        patient_row(page, patient).wait_for(state="visible", timeout=20000)
        delete_patient(page, flow, patient)