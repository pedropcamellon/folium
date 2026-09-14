"""Public API evaluation lifecycle coverage."""

import asyncio
import json
from pathlib import Path

import httpx

from app.e2e_eval_runner import EvaluationSettings, evaluate_case


def test_evaluation_exercises_the_public_lifecycle(tmp_path: Path) -> None:
    case_path = tmp_path / "case.yaml"
    case_path.write_text(
        """id: test-lifecycle
title: Evaluator lifecycle
version: 1
description: Minimal synthetic lifecycle contract.
metadata:
  evaluation_pack: test-pack
  clinical_area: test-area
  condition: test-condition
  scenario: lifecycle
fixture:
  patient:
    key: test-patient
    age_at_active_encounter: 50
    date_of_birth: 1976-01-01
    gender: unspecified
  encounters:
    - key: active
      occurred_at: 2026-01-01T10:00:00Z
      title: Synthetic active encounter
      note: Required summary fact.
  active_encounter_key: active
expected:
  output:
    summary_facts: [Required summary fact.]
    missing_information: []
    follow_up_questions: []
    required_source_roles: [active.note]
  history_decision:
    should_retrieve: false
    expected_returned_source_roles: []
  validation:
    expected_status: valid
""",
        encoding="utf-8",
    )
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/auth/jwt/login":
            return httpx.Response(200, json={"access_token": "test-token"})
        if request.url.path == "/api/v1/patients/":
            return httpx.Response(201, json={"id": "patient-id"})
        if request.url.path == "/api/v1/encounters/":
            return httpx.Response(201, json={"id": "active-id"})
        if request.url.path == "/api/v1/encounters/active-id/narratives":
            return httpx.Response(201, json={"id": "narrative-id"})
        if (
            request.url.path == "/api/v1/encounters/active-id/chart-review"
            and request.method == "POST"
        ):
            return httpx.Response(200, json={"status": "queued"})
        if request.url.path == "/api/v1/encounters/active-id/chart-review":
            return httpx.Response(
                200,
                json={
                    "id": "review-id",
                    "status": "completed",
                    "summary": "Required summary fact.",
                    "reasoning": "The active note supplies the required fact.",
                    "missingInfo": [],
                    "followUpQuestions": [],
                },
            )
        if (
            request.url.path
            == "/api/v1/encounters/internal/chart-review/review-id/evaluation-evidence"
        ):
            assert request.headers["X-ChartReview-Internal-Token"] == "internal-token"
            assert request.headers["X-ChartReview-Evaluation-Token"] == "evaluation-token"
            return httpx.Response(
                200,
                json={
                    "reviewId": "review-id",
                    "status": "completed",
                    "inputSourceIds": ["encounter-note:active-id"],
                    "citedSourceIds": ["encounter-note:active-id"],
                },
            )
        if request.url.path == "/api/v1/patients/patient-id" and request.method == "DELETE":
            return httpx.Response(204)
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    result = asyncio.run(
        evaluate_case(
            case_path,
            EvaluationSettings(
                "http://testserver",
                None,
                "eval@example.test",
                "test",
                0,
                1,
                tmp_path / "artifacts",
                internal_token="internal-token",
                evaluation_token="evaluation-token",
            ),
            transport=httpx.MockTransport(respond),
        )
    )

    assert result.passed is True
    assert [(axis.name, axis.passed) for axis in result.axes] == [
        ("validation", True),
        ("draft", True),
        ("retrieval", True),
        ("provenance", True),
    ]
    assert [request.method for request in requests] == [
        "POST",
        "POST",
        "POST",
        "POST",
        "POST",
        "GET",
        "GET",
        "DELETE",
    ]
    encounter_payloads = [
        json.loads(request.content)
        for request in requests
        if request.url.path == "/api/v1/encounters/"
    ]
    assert [payload["purpose"] for payload in encounter_payloads] == ["follow_up"]
