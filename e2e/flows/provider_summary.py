from __future__ import annotations

from flow_cases import FlowCase
from mocks import install_summary_page_mocks, remove_summary_page_mocks
from playwright.sync_api import Page
from settings import SUMMARY_WAIT_MS
from ui import (
    close_interaction_details,
    generate_and_assert_summary,
    open_interaction_details,
)


def run_provider_summary_flow(
    page: Page, base_url: str, flow: FlowCase, transcript: str
) -> None:
    patient_id, interaction_title, routes = install_summary_page_mocks(page, transcript)
    try:
        page.goto(f"{base_url}/patients/{patient_id}", wait_until="domcontentloaded")
        page.get_by_text("Taylor Summary", exact=True).wait_for(
            state="visible", timeout=15000
        )
        open_interaction_details(page, flow, interaction_title)
        generate_and_assert_summary(page, flow, timeout_ms=SUMMARY_WAIT_MS)
        close_interaction_details(page)
    finally:
        remove_summary_page_mocks(page, routes)
