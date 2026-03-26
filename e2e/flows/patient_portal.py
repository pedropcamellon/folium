from __future__ import annotations

from playwright.sync_api import Page

from flow_cases import FlowCase


def run_patient_portal_flow(page: Page, base_url: str, flow: FlowCase) -> None:
    return