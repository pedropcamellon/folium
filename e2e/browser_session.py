from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from flow_cases import FlowCase
from ui import login, logout, verify_landing
from ui.session import log_step


def run_flow(
    page: Page,
    base_url: str,
    flow: FlowCase,
    scenario_name: str,
    post_login_runner,
) -> None:
    try:
        login(page, base_url, flow)
        verify_landing(page, flow)

        post_login_runner(page, base_url, flow)

        if flow.wait_after_login_ms > 0:
            log_step(flow.name, f"Pausing for {flow.wait_after_login_ms}ms")
            page.wait_for_timeout(flow.wait_after_login_ms)

        logout(page, flow)
        log_step(flow.name, f"Scenario passed: {scenario_name}")
    except PlaywrightTimeoutError as exc:
        raise AssertionError(
            f"Timed out during {scenario_name} scenario: {exc}"
        ) from exc
