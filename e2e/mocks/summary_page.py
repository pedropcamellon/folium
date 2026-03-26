from __future__ import annotations

import json

from playwright.sync_api import Page, Route

RoutePatterns = tuple[str, ...]


def install_summary_page_mocks(
    page: Page, transcript: str
) -> tuple[str, str, RoutePatterns]:
    patient_id = "00000000-0000-0000-0000-000000000101"
    interaction_id = "00000000-0000-0000-0000-000000000201"
    patient_url = f"**/api/v1/patients/{patient_id}"
    interactions_url = f"**/api/v1/interactions/?patientId={patient_id}"
    interaction_url = f"**/api/v1/interactions/{interaction_id}"
    documents_url = f"**/api/v1/clinical-documents/?patientId={patient_id}*"

    patient_payload = {
        "id": patient_id,
        "medicalRecordNumber": "E2E-SUMMARY-001",
        "firstName": "Taylor",
        "lastName": "Summary",
        "dateOfBirth": "1992-04-15",
        "gender": "Female",
        "contactInfo": "taylor.summary@southdrift.test",
        "medicalImages": [],
        "clinicalSummaries": [],
    }
    interaction_payload = {
        "id": interaction_id,
        "createdAt": "2026-03-26T10:00:00Z",
        "createdBy": "provider@southdrift.com",
        "description": "Mocked summary scenario interaction.",
        "interactionDate": "2026-03-26T10:00:00Z",
        "isCompliant": True,
        "location": "Mock Clinic",
        "metadata": {},
        "note": transcript,
        "summary": "",
        "patientId": patient_id,
        "providerId": "provider-001",
        "providerName": "Dr. SouthDrift",
        "title": "Mock Summary Interaction",
        "type": "VoiceNote",
        "updatedAt": "2026-03-26T10:00:00Z",
        "updatedBy": "provider@southdrift.com",
    }
    route_patterns = (patient_url, interactions_url, interaction_url, documents_url)

    def handle_patient(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(patient_payload),
        )

    def handle_interactions(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps([interaction_payload]),
        )

    def handle_interaction(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(interaction_payload),
        )

    def handle_documents(route: Route) -> None:
        route.fulfill(status=200, content_type="application/json", body="[]")

    page.route(patient_url, handle_patient)
    page.route(interactions_url, handle_interactions)
    page.route(interaction_url, handle_interaction)
    page.route(documents_url, handle_documents)

    return patient_id, interaction_payload["title"], route_patterns


def remove_summary_page_mocks(page: Page, routes: RoutePatterns) -> None:
    for route_url in routes:
        page.unroute(route_url)
