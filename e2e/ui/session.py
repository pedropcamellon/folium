from __future__ import annotations

from playwright.sync_api import Browser, Page

from flow_cases import FlowCase


def log_step(flow_name: str, message: str) -> None:
    print(f"[{flow_name}] {message}")


def login(page: Page, base_url: str, flow: FlowCase) -> None:
    log_step(flow.name, "Opening login page")
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")

    page.get_by_label("Email").fill(flow.email)
    page.get_by_label("Password").fill(flow.password)

    log_step(flow.name, "Submitting credentials")
    page.get_by_role("button", name="Login").click()


def verify_landing(page: Page, flow: FlowCase) -> None:
    log_step(flow.name, f"Waiting for redirect to {flow.expected_path}")
    page.wait_for_url(f"**{flow.expected_path}", timeout=20000)

    log_step(flow.name, f"Verifying heading '{flow.expected_heading}'")
    page.get_by_role("heading", name=flow.expected_heading).wait_for(
        state="visible", timeout=15000
    )


def logout(page: Page, flow: FlowCase) -> None:
    log_step(flow.name, "Opening account menu")
    page.locator("header").locator("button").filter(has_text=flow.email).first.click(
        timeout=15000
    )

    log_step(flow.name, "Logging out")
    page.get_by_role("menuitem", name="Logout").click(timeout=15000)
    page.wait_for_url("**/login", timeout=15000)


def new_page(browser: Browser, base_url: str) -> Page:
    context = browser.new_context()
    context.grant_permissions(["microphone"], origin=base_url)
    return context.new_page()