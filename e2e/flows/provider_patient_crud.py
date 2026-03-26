from __future__ import annotations

from playwright.sync_api import Page

from flow_cases import FlowCase
from patient_payloads import build_provider_test_patient, build_updated_patient
from ui import create_patient, delete_patient, update_patient


def run_provider_patient_crud(page: Page, base_url: str, flow: FlowCase) -> None:
    patient = build_provider_test_patient()
    updated_patient = build_updated_patient(patient)

    create_patient(page, flow, patient)
    update_patient(page, flow, patient, updated_patient)
    delete_patient(page, flow, updated_patient)