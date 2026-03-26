from __future__ import annotations

import json

from playwright.sync_api import Page, Route


RoutePatterns = tuple[str, str, str, str]


def install_interaction_mocks(
    page: Page, interaction_id: str, transcript: str
) -> RoutePatterns:
    interaction_url = f"**/api/v1/interactions/{interaction_id}"
    audio_url = f"**/api/v1/interactions/{interaction_id}/audio"
    note_url = f"**/api/v1/interactions/{interaction_id}/note"
    summarize_url = "**/api/v1/summarization/test"
    state = {
        "transcribed_note": "",
        "saved_note": "",
    }

    def handle_interaction(route: Route) -> None:
        response = route.fetch()
        data = response.json()

        note_value = state["saved_note"] or state["transcribed_note"]
        if note_value:
            data["note"] = note_value

        route.fulfill(response=response, json=data)

    def handle_audio(route: Route) -> None:
        state["transcribed_note"] = transcript
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"message": "Audio accepted"}),
        )

    def handle_note(route: Route) -> None:
        payload = route.request.post_data_json
        state["saved_note"] = payload.get("note", "")
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"note": state["saved_note"]}),
        )

    def handle_summary(route: Route) -> None:
        payload = route.request.post_data_json
        note = payload.get("transcript", "")
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "summary": "SOAP summary generated in e2e",
                    "structured_data": {
                        "chief_complaint": "Improved sleep and residual cough",
                        "subjective": note,
                        "objective": "Afebrile and speaking clearly during follow-up.",
                        "assessment": "Upper respiratory symptoms are improving.",
                        "plan": "Continue hydration, monitor cough, and follow up if symptoms worsen.",
                        "clinical_tags": ["follow-up", "respiratory"],
                        "icd_codes": ["J06.9"],
                        "action_items": [
                            "Continue supportive care",
                            "Return if fever recurs",
                        ],
                    },
                    "processing_time": 0.25,
                    "model_used": "playwright-e2e",
                    "provider": "mock",
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 1,
                        "total_tokens": 2,
                    },
                }
            ),
        )

    page.route(interaction_url, handle_interaction)
    page.route(audio_url, handle_audio)
    page.route(note_url, handle_note)
    page.route(summarize_url, handle_summary)
    return interaction_url, audio_url, note_url, summarize_url


def remove_interaction_mocks(page: Page, routes: RoutePatterns) -> None:
    for route_url in routes:
        page.unroute(route_url)