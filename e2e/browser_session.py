from __future__ import annotations

from playwright.sync_api import Browser, Page, TimeoutError as PlaywrightTimeoutError

from flow_cases import FlowCase
from patient_payloads import PatientPayload, build_provider_test_patient, build_updated_patient


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


def open_add_patient_dialog(page: Page) -> None:
    page.get_by_role("button", name="Add Patient").click(timeout=15000)
    page.get_by_role("heading", name="Add New Patient").wait_for(
        state="visible", timeout=15000
    )


def fill_patient_form(page: Page, patient: PatientPayload) -> None:
    page.get_by_placeholder("MRN").fill(patient.medical_record_number)
    page.get_by_placeholder("First Name").fill(patient.first_name)
    page.get_by_placeholder("Last Name").fill(patient.last_name)
    page.locator('input[name="dateOfBirth"]').fill(patient.date_of_birth)
    page.locator('select[name="gender"]').select_option(patient.gender)
    page.get_by_placeholder("Contact Info").fill(patient.contact_info)


def patient_row(page: Page, patient: PatientPayload):
    return page.get_by_role("row").filter(
        has=page.get_by_text(patient.medical_record_number, exact=True)
    )


def create_patient(page: Page, flow: FlowCase, patient: PatientPayload) -> None:
    log_step(flow.name, f"Creating patient {patient.full_name}")
    open_add_patient_dialog(page)
    fill_patient_form(page, patient)
    page.get_by_role("button", name="Add Patient").last.click(timeout=15000)
    patient_row(page, patient).wait_for(state="visible", timeout=20000)


def update_patient(
    page: Page,
    flow: FlowCase,
    original_patient: PatientPayload,
    updated_patient: PatientPayload,
) -> None:
    log_step(flow.name, f"Updating patient {original_patient.full_name}")
    row = patient_row(page, original_patient)
    row.get_by_role("button", name="Edit").click(timeout=15000)
    page.get_by_role("heading", name="Edit Patient").wait_for(
        state="visible", timeout=15000
    )
    fill_patient_form(page, updated_patient)
    page.get_by_role("button", name="Update Patient").click(timeout=15000)
    updated_row = patient_row(page, updated_patient)
    updated_row.wait_for(state="visible", timeout=20000)
    updated_row.get_by_text(updated_patient.contact_info, exact=True).wait_for(
        state="visible", timeout=15000
    )


def delete_patient(page: Page, flow: FlowCase, patient: PatientPayload) -> None:
    log_step(flow.name, f"Deleting patient {patient.full_name}")
    row = patient_row(page, patient)
    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name="Delete").click(timeout=15000)
    row.wait_for(state="detached", timeout=20000)


def run_provider_patient_crud(page: Page, flow: FlowCase) -> None:
    patient = build_provider_test_patient()
    updated_patient = build_updated_patient(patient)

    create_patient(page, flow, patient)
    update_patient(page, flow, patient, updated_patient)
    delete_patient(page, flow, updated_patient)


def logout(page: Page, flow: FlowCase) -> None:
    log_step(flow.name, "Opening account menu")
    page.locator("header").locator("button").filter(has_text=flow.email).first.click(
        timeout=15000
    )

    log_step(flow.name, "Logging out")
    page.get_by_role("menuitem", name="Logout").click(timeout=15000)
    page.wait_for_url("**/login", timeout=15000)


def run_flow(page: Page, base_url: str, flow: FlowCase) -> None:
    try:
        login(page, base_url, flow)
        verify_landing(page, flow)

        if flow.name == "provider":
            run_provider_patient_crud(page, flow)

        if flow.wait_after_login_ms > 0:
            log_step(flow.name, f"Pausing for {flow.wait_after_login_ms}ms")
            page.wait_for_timeout(flow.wait_after_login_ms)

        logout(page, flow)
        log_step(flow.name, "Flow passed")
    except PlaywrightTimeoutError as exc:
        raise AssertionError(f"Timed out during {flow.name} flow: {exc}") from exc


def new_page(browser: Browser) -> Page:
    context = browser.new_context()
    return context.new_page()
