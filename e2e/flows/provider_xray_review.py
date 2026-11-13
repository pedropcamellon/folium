from __future__ import annotations

import math
import os
import re
import struct
import zlib
from pathlib import Path

from flow_cases import FlowCase
from patient_payloads import build_provider_test_patient
from playwright.sync_api import Page, expect
from ui import create_patient, delete_patient, open_patient_history, patient_row
from ui.session import log_step


def run_provider_xray_review_flow(
    page: Page, base_url: str, flow: FlowCase
) -> None:
    patient = build_provider_test_patient()
    title = "Synthetic chest phantom - not a clinical X-ray"
    screenshot = Path(
        os.getenv(
            "FOLIUM_XRAY_SCREENSHOT", "/tmp/folium-e2e/xray-review-ready.png"
        )
    )
    wait_ms = int(os.getenv("FOLIUM_XRAY_WAIT_MS", "180000"))
    page.get_by_role("link", name="Imaging AI", exact=True).click()
    expect(page).to_have_url(f"{base_url}/imaging")
    expect(page.get_by_role("heading", name="Imaging AI", exact=True)).to_be_visible()
    create_patient(page, flow, patient)
    try:
        page.set_viewport_size({"width": 1600, "height": 1100})
        open_patient_history(page, flow, patient)
        chart_url = page.url
        page.get_by_role("button", name="Upload Document", exact=True).click()
        dialog = page.get_by_role("dialog")
        dialog.locator('input[type="file"]').set_input_files(
            {
                "name": "synthetic-chest-phantom.png",
                "mimeType": "image/png",
                "buffer": _synthetic_chest_png(),
            }
        )
        dialog.get_by_role("combobox").click()
        page.get_by_role("option", name="X-ray Image", exact=True).click()
        dialog.get_by_label("Title").fill(title)
        with page.expect_response(
            lambda response: response.request.method == "POST"
            and "/clinical-documents/upload" in response.url
        ) as uploaded:
            dialog.get_by_role("button", name="Upload Document", exact=True).click()
        assert uploaded.value.ok, uploaded.value.text()
        expect(dialog).not_to_be_visible(timeout=20000)

        def open_review() -> None:
            row = page.get_by_role("listitem").filter(
                has=page.get_by_text(title, exact=True)
            )
            row.get_by_role("button", name="View document").click()
            page.get_by_role("button", name="X-ray review", exact=True).click()
            expect(page).to_have_url(
                re.compile(r"/patients/[^/]+/documents/[^/]+/xray-review$")
            )
            expect(page.get_by_role("dialog")).not_to_be_visible()
            image = page.get_by_role("img", name=title, exact=True)
            expect(image).to_be_visible(timeout=20000)
            expect(image).to_have_js_property("complete", True)
            assert image.evaluate("(image) => image.naturalWidth > 0")

        open_review()
        review_url = page.url
        page.get_by_role("button", name="Run scan", exact=True).click()
        terminal = page.get_by_text(
            re.compile(r"^Scan status: (COMPLETE|FAILED)$")
        )
        expect(terminal).to_be_visible(timeout=wait_ms)
        assert terminal.inner_text() == "Scan status: COMPLETE", (
            page.locator("aside").inner_text()
        )
        expect(page.get_by_text("Needs provider review", exact=True)).to_be_visible()
        expect(page.get_by_text("This model does not diagnose", exact=False)).to_be_visible()
        table = page.get_by_role("table")
        expect(table.get_by_role("row")).to_have_count(14)
        expect(table).not_to_contain_text("No Finding")
        expect(table).to_contain_text("%")
        findings = table.inner_text()
        page.get_by_role("button", name="Back to patient", exact=True).click()
        expect(page).to_have_url(chart_url)
        expect(page.get_by_text("Needs provider review", exact=True)).not_to_be_visible()
        open_review()
        expect(page).to_have_url(review_url)
        expect(table).to_have_text(findings, use_inner_text=True, timeout=20000)
        page.reload(wait_until="domcontentloaded")
        expect(table).to_have_text(findings, use_inner_text=True, timeout=20000)
        expect(page.get_by_role("button", name="Run again", exact=True)).to_be_visible()
        expect(page.get_by_role("img", name=title)).to_have_js_property("complete", True)
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
        log_step(flow.name, f"Real inference and persisted review verified: {screenshot}")
    finally:
        page.goto(f"{base_url}{flow.expected_path}", wait_until="domcontentloaded")
        patient_row(page, patient).wait_for(state="visible", timeout=20000)
        delete_patient(page, flow, patient)


def _synthetic_chest_png() -> bytes:
    """Generate an artificial chest phantom, never patient image data."""
    width, height = 384, 512
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            nx, ny = (x - width / 2) / 150, (y - height / 2) / 215
            body = nx * nx + ny * ny < 1
            lung = min(
                ((nx - side) / 0.34) ** 2 + ((ny + 0.08) / 0.72) ** 2
                for side in (-0.43, 0.43)
            ) < 1
            value = 110 if body else 12
            if lung:
                value = 38 + int(22 * (1 + math.cos(ny * 52 + nx * nx * 8)))
            if body and abs(nx) < 0.08:
                value = 175
            pixels.append(value)

    def chunk(kind: bytes, content: bytes) -> bytes:
        return (
            struct.pack(">I", len(content))
            + kind
            + content
            + struct.pack(">I", zlib.crc32(kind + content))
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(pixels)))
        + chunk(b"IEND", b"")
    )
