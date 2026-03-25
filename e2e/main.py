from __future__ import annotations

from playwright.sync_api import sync_playwright

from browser_session import new_page, run_flow
from flow_cases import PATIENT_FLOW, PROVIDER_FLOW, FlowCase
from settings import BASE_URL, HEADLESS, PROVIDER_WAIT_MS, SLOW_MO_MS


def with_provider_pause(flow: FlowCase, wait_ms: int) -> FlowCase:
    return FlowCase(
        name=flow.name,
        email=flow.email,
        password=flow.password,
        expected_path=flow.expected_path,
        expected_heading=flow.expected_heading,
        expected_identity_text=flow.expected_identity_text,
        wait_after_login_ms=wait_ms,
    )


def main() -> None:
    print(f"Running SouthDrift role-flow checks against {BASE_URL}")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO_MS,
        )
        page = new_page(browser)
        try:
            run_flow(
                page,
                BASE_URL,
                with_provider_pause(PROVIDER_FLOW, PROVIDER_WAIT_MS),
            )
            run_flow(page, BASE_URL, PATIENT_FLOW)
        finally:
            page.context.close()
            browser.close()

    print("All requested user flows passed")


if __name__ == "__main__":
    main()
