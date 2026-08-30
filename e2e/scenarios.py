from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

from flow_cases import PATIENT_FLOW, PROVIDER_FLOW, FlowCase
from flows.patient_portal import run_patient_portal_flow
from flows.provider_chart_review import run_provider_chart_review_flow
from flows.provider_patient_crud import run_provider_patient_crud
from flows.provider_summary import run_provider_summary_flow
from flows.provider_voice_note import run_provider_voice_note_flow
from playwright.sync_api import Page
from settings import FAKE_TRANSCRIPT, PROVIDER_WAIT_MS

ScenarioRunner = Callable[[Page, str, FlowCase], None]


@dataclass(frozen=True)
class Scenario:
    name: str
    flow: FlowCase
    runner: ScenarioRunner


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


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        name="provider-patient-crud",
        flow=with_provider_pause(PROVIDER_FLOW, PROVIDER_WAIT_MS),
        runner=run_provider_patient_crud,
    ),
    Scenario(
        name="provider-chart-review",
        flow=with_provider_pause(PROVIDER_FLOW, PROVIDER_WAIT_MS),
        runner=run_provider_chart_review_flow,
    ),
    Scenario(
        name="provider-voice-note",
        flow=with_provider_pause(PROVIDER_FLOW, PROVIDER_WAIT_MS),
        runner=lambda page, base_url, flow: run_provider_voice_note_flow(
            page, base_url, flow, FAKE_TRANSCRIPT
        ),
    ),
    Scenario(
        name="provider-summary",
        flow=with_provider_pause(PROVIDER_FLOW, PROVIDER_WAIT_MS),
        runner=lambda page, base_url, flow: run_provider_summary_flow(
            page, base_url, flow, FAKE_TRANSCRIPT
        ),
    ),
    Scenario(
        name="patient-portal",
        flow=PATIENT_FLOW,
        runner=run_patient_portal_flow,
    ),
)


SCENARIO_BY_NAME = {scenario.name: scenario for scenario in SCENARIOS}


def resolve_scenarios(requested_names: list[str] | None = None) -> list[Scenario]:
    names = requested_names or _scenario_names_from_env()
    if not names:
        return list(SCENARIOS)

    resolved: list[Scenario] = []
    for name in names:
        scenario = SCENARIO_BY_NAME.get(name)
        if scenario is None:
            available = ", ".join(SCENARIO_BY_NAME)
            raise ValueError(f"Unknown scenario '{name}'. Available: {available}")
        resolved.append(scenario)

    return resolved


def _scenario_names_from_env() -> list[str]:
    raw = os.getenv("FOLIUM_E2E_SCENARIOS", "").strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]
