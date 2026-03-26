from __future__ import annotations

from playwright.sync_api import Page

from flow_cases import FlowCase

from .session import log_step


def create_interaction(page: Page, flow: FlowCase, title: str) -> str:
    log_step(flow.name, f"Creating interaction {title}")
    page.get_by_role("button", name="New Interaction").click(timeout=15000)
    page.get_by_role("heading", name="Add New Interaction").wait_for(
        state="visible", timeout=15000
    )

    page.locator("#type").click(timeout=15000)
    page.get_by_role("option", name="Voice Note").click(timeout=15000)
    page.get_by_label("Title").fill(title)
    page.get_by_label("Description").fill(
        "Provider voice note workflow created by Playwright."
    )
    page.get_by_label("Provider Name").fill("Dr. SouthDrift")

    with page.expect_response(
        lambda response: response.request.method == "POST"
        and "/api/v1/interactions" in response.url
        and response.status == 201,
        timeout=20000,
    ) as response_info:
        page.get_by_role("button", name="Create Interaction").click(timeout=15000)

    interaction = response_info.value.json()
    page.get_by_role("button", name=f"View details for {title}").wait_for(
        state="visible", timeout=20000
    )
    return interaction["id"]


def open_interaction_details(page: Page, flow: FlowCase, title: str) -> None:
    log_step(flow.name, f"Opening interaction details for {title}")
    page.get_by_role("button", name=f"View details for {title}").click(timeout=15000)
    page.get_by_role("heading", name="Interaction Details").wait_for(
        state="visible", timeout=15000
    )


def record_and_submit_audio(page: Page, flow: FlowCase, transcript: str) -> None:
    log_step(flow.name, "Recording and submitting audio")
    page.get_by_role("button", name="Record").click(timeout=15000)
    page.get_by_role("button", name="Stop Recording").wait_for(
        state="visible", timeout=15000
    )
    page.wait_for_timeout(1500)
    page.get_by_role("button", name="Stop Recording").click(timeout=15000)
    page.get_by_role("button", name="Submit Audio").wait_for(
        state="visible", timeout=15000
    )
    page.get_by_role("button", name="Submit Audio").click(timeout=15000)

    page.get_by_text("Transcription complete!", exact=True).wait_for(
        state="visible", timeout=15000
    )
    page.get_by_text(transcript, exact=True).wait_for(state="visible", timeout=15000)


def edit_and_save_note(page: Page, flow: FlowCase, note: str) -> None:
    log_step(flow.name, "Editing and saving transcribed note")
    page.get_by_role("button", name="Edit Note").click(timeout=15000)
    note_editor = page.locator("textarea").first
    note_editor.fill(note)
    page.get_by_role("button", name="Save").click(timeout=15000)
    page.get_by_text(note, exact=True).wait_for(state="visible", timeout=15000)


def generate_and_assert_summary(page: Page, flow: FlowCase) -> None:
    log_step(flow.name, "Generating summary from saved note")
    page.get_by_role("button", name="Generate Summary").click(timeout=15000)
    page.get_by_text("Chief Complaint: Improved sleep and residual cough").wait_for(
        state="visible", timeout=15000
    )
    page.get_by_text("Plan:", exact=False).wait_for(state="visible", timeout=15000)


def close_interaction_details(page: Page) -> None:
    page.get_by_role("button", name="Close").click(timeout=15000)