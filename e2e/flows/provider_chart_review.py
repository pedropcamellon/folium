from __future__ import annotations

import re

from flow_cases import FlowCase
from playwright.sync_api import Page, expect
from settings import CHART_REVIEW_WAIT_MS
from ui import close_interaction_details, open_interaction_details
from ui.session import log_step

SEEDED_PATIENT_ID = "8b82386f-673d-4947-944a-421bd57c8e41"
FOLLOW_UP_TITLE = "Follow-up Visit - Cough Improvement"


def run_provider_chart_review_flow(page: Page, base_url: str, flow: FlowCase) -> None:
    """Run the real local chart-review workflow against a synthetic seeded interaction."""
    log_step(flow.name, "Opening seeded follow-up interaction for chart review")
    page.goto(f"{base_url}/patients/{SEEDED_PATIENT_ID}", wait_until="domcontentloaded")
    open_interaction_details(page, flow, FOLLOW_UP_TITLE)

    dialog = page.get_by_role("dialog")
    dialog.get_by_role("button", name=re.compile(r"Generate (new )?draft")).click(
        timeout=15000
    )
    dialog.get_by_text("Draft review is processing.", exact=True).wait_for(
        state="visible", timeout=15000
    )
    expect(dialog.get_by_role("heading", name="Review rationale")).to_have_count(0)
    expect(dialog.get_by_role("heading", name="Source references")).to_have_count(0)
    expect(dialog.get_by_text("Confidence:", exact=False)).to_have_count(0)
    dialog.get_by_text("Draft review is processing.", exact=True).wait_for(
        state="hidden", timeout=CHART_REVIEW_WAIT_MS
    )

    dialog.get_by_text("Confidence:", exact=False).wait_for(
        state="visible", timeout=15000
    )
    expect(
        dialog.locator(
            "section[aria-labelledby='chart-review-heading'] > div:last-child > p"
        )
    ).not_to_be_empty(timeout=15000)
    dialog.get_by_role("heading", name="Source references").wait_for(
        state="visible", timeout=15000
    )
    dialog.get_by_text(
        "Follow-up Visit - Cough Improvement - summary", exact=True
    ).wait_for(state="visible", timeout=15000)
    expect(dialog.get_by_text("interaction-summary:", exact=False)).to_have_count(0)
    dialog.get_by_role("heading", name="Review rationale").wait_for(
        state="visible", timeout=15000
    )
    close_interaction_details(page)
