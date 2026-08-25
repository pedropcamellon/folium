from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FlowCase:
    name: str
    email: str
    password: str
    expected_path: str
    expected_heading: str
    expected_identity_text: str | None = None
    wait_after_login_ms: int = 0


PROVIDER_FLOW = FlowCase(
    name="provider",
    email=os.getenv("FOLIUM_PROVIDER_EMAIL", "provider@folium.com"),
    password=os.getenv("FOLIUM_PROVIDER_PASSWORD", "Provider123!"),
    expected_path="/provider",
    expected_heading="Provider Portal",
)

PATIENT_FLOW = FlowCase(
    name="patient",
    email=os.getenv("FOLIUM_PATIENT_EMAIL", "patient@folium.com"),
    password=os.getenv("FOLIUM_PATIENT_PASSWORD", "Patient123!"),
    expected_path="/portal",
    expected_heading="Patient Portal",
)
