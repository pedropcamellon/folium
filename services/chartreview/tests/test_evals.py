"""Fast request-sequence coverage for chart-review evaluation cases."""

import asyncio
import json
import os
from pathlib import Path

import httpx

from app.e2e_eval_runner import (
    EvaluationSettings,
    evaluate_case,
    score_review_axes,
)
from app.evals import ChartReviewBenchmarkCase

os.environ.setdefault("AI_SERVICE_BASE_URL", "http://localhost:8002")
os.environ.setdefault("CHARTREVIEW_BACKEND_URL", "http://localhost:8000")
os.environ.setdefault("CHARTREVIEW_INTERNAL_TOKEN", "test-token")

from folium.core.chart_review import ChartReviewInput, ChartReviewSourceChunk, ChartReviewSourceType

from app.graph import _format_active_context


def _case(
    *,
    should_retrieve: bool = False,
    forbidden_search_terms: list[str] | None = None,
    follow_up_questions: list[str] | None = None,
    required_follow_up_terms: list[str] | None = None,
    forbidden_follow_up_terms: list[str] | None = None,
) -> ChartReviewBenchmarkCase:
    return ChartReviewBenchmarkCase.model_validate(
        {
            "id": "test-case",
            "title": "Evaluator behavior test",
            "version": 1,
            "description": "Minimal synthetic evaluator contract.",
            "metadata": {
                "evaluation_pack": "test-pack",
                "clinical_area": "test-area",
                "condition": "test-condition",
                "scenario": "test-scenario",
            },
            "fixture": {
                "patient": {
                    "key": "test-patient",
                    "age_at_active_encounter": 50,
                    "date_of_birth": "1976-01-01",
                    "gender": "unspecified",
                },
                "encounters": [
                    {
                        "key": "active",
                        "occurred_at": "2026-01-01T10:00:00Z",
                        "title": "Synthetic active encounter",
                        "note": "Required summary fact.",
                    }
                ],
                "active_encounter_key": "active",
            },
            "expected": {
                "output": {
                    "summary_facts": ["Required summary fact."],
                    "missing_information": [],
                    "follow_up_questions": follow_up_questions or [],
                    "required_follow_up_terms": required_follow_up_terms or [],
                    "forbidden_follow_up_terms": forbidden_follow_up_terms or [],
                    "required_source_roles": ["active.note"],
                },
                "history_decision": {
                    "should_retrieve": should_retrieve,
                    "forbidden_search_terms": forbidden_search_terms or [],
                },
                "validation": {"expected_status": "valid"},
            },
        }
    )


def test_refined_case_follow_up_terms_reject_irrelevant_questions() -> None:
    case = _case(
        follow_up_questions=["Expected follow-up question."],
        forbidden_follow_up_terms=["change"],
    )

    axes = score_review_axes(
        case,
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "followUpQuestions": ["Should the record change?"],
        },
    )

    draft_axis = next(axis for axis in axes if axis.name == "draft")
    assert draft_axis.failures == ["follow-up questions included forbidden term: change"]


def test_active_context_prioritizes_the_final_narrative_without_omitting_encounter_fields() -> None:
    review_input = ChartReviewInput(
        patient_id="patient-001",
        encounter_id="encounter-001",
        encounters=[
            ChartReviewSourceChunk(
                source_id="encounter-title:encounter-001",
                source_type=ChartReviewSourceType.ENCOUNTER,
                content="Current encounter",
                content_role="title",
            )
        ],
        transcript=ChartReviewSourceChunk(
            source_id="encounter-note:encounter-001",
            source_type=ChartReviewSourceType.TRANSCRIPT,
            content="Cough, nasal congestion, and fever are present.",
            content_role="voice-note transcript",
        ),
    )

    context = _format_active_context(review_input)

    assert context.index("encounter-note:encounter-001") < context.index(
        "encounter-title:encounter-001"
    )
    assert "primary current-state source" in context
    assert "Additional active encounter context" in context


def test_score_review_rejects_unexpected_history_lookup() -> None:
    case = _case(forbidden_search_terms=["unnecessary"])

    axes = score_review_axes(
        case,
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "missingInfo": [],
            "followUpQuestions": [],
            "historySearchTerms": ["unnecessary"],
            "historyResults": [],
        },
    )

    retrieval_axis = next(axis for axis in axes if axis.name == "retrieval")
    assert retrieval_axis.failures == [
        "history retrieval was requested when no lookup was expected",
        "history retrieval included forbidden search term: unnecessary",
    ]


def test_score_review_reports_retrieval_as_an_independent_axis() -> None:
    axes = score_review_axes(
        _case(),
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "missingInfo": [],
            "followUpQuestions": [],
            "historySearchTerms": ["unnecessary"],
            "historyResults": [],
        },
    )

    assert [(axis.name, axis.passed) for axis in axes] == [
        ("validation", True),
        ("draft", True),
        ("retrieval", False),
    ]


def test_score_review_rejects_questions_for_complete_context() -> None:
    axes = score_review_axes(
        _case(),
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "followUpQuestions": ["Can you provide another fact?"],
        },
    )

    draft_axis = next(axis for axis in axes if axis.name == "draft")
    assert draft_axis.failures == ["follow-up questions were returned when none were expected"]


def test_patient_001_exercises_the_public_evaluation_lifecycle(tmp_path: Path) -> None:
    case_path = tmp_path / "case.yaml"
    case_path.write_text(
        """id: test-lifecycle\ntitle: Evaluator lifecycle\nversion: 1\ndescription: Minimal synthetic lifecycle contract.\nmetadata:\n  evaluation_pack: test-pack\n  clinical_area: test-area\n  condition: test-condition\n  scenario: lifecycle\nfixture:\n  patient:\n    key: test-patient\n    age_at_active_encounter: 50\n    date_of_birth: 1976-01-01\n    gender: unspecified\n  encounters:\n    - key: active\n      occurred_at: 2026-01-01T10:00:00Z\n      title: Synthetic active encounter\n      note: Required summary fact.\n  active_encounter_key: active\nexpected:\n  output:\n    summary_facts: [Required summary fact.]\n    missing_information: []\n    follow_up_questions: []\n    required_source_roles: [active.note]\n  history_decision:\n    should_retrieve: false\n    expected_returned_source_roles: []\n  validation:\n    expected_status: valid\n""",
        encoding="utf-8",
    )
    environment_file = tmp_path / ".env"
    environment_file.write_text(
        "UNRELATED_SERVICE_VALUE=ignored\n"
        "FOLIUM_EVAL_USER_EMAIL=eval@example.test\n"
        "FOLIUM_EVAL_USER_PASSWORD=test\n",
        encoding="utf-8",
    )
    previous_email = os.environ.pop("FOLIUM_EVAL_USER_EMAIL", None)
    previous_password = os.environ.pop("FOLIUM_EVAL_USER_PASSWORD", None)
    try:
        settings = EvaluationSettings.from_environment(environment_file)
    finally:
        if previous_email is not None:
            os.environ["FOLIUM_EVAL_USER_EMAIL"] = previous_email
        if previous_password is not None:
            os.environ["FOLIUM_EVAL_USER_PASSWORD"] = previous_password

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
                    "status": "completed",
                    "summary": "Required summary fact.",
                    "reasoning": "The active note supplies the required fact.",
                    "missingInfo": [],
                    "followUpQuestions": [],
                },
            )
        if request.url.path == "/api/v1/patients/patient-id" and request.method == "DELETE":
            return httpx.Response(204)
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    result = asyncio.run(
        evaluate_case(
            case_path,
            EvaluationSettings(
                "http://testserver", None, settings.user_email, settings.user_password, 0, 1
            ),
            transport=httpx.MockTransport(respond),
        )
    )

    assert result.passed is True
    assert [(axis.name, axis.passed) for axis in result.axes] == [
        ("validation", True),
        ("draft", True),
        ("retrieval", True),
    ]
    assert [request.method for request in requests] == [
        "POST",
        "POST",
        "POST",
        "POST",
        "POST",
        "GET",
        "DELETE",
    ]
    encounter_payloads = [
        json.loads(request.content)
        for request in requests
        if request.url.path == "/api/v1/encounters/"
    ]
    assert [payload["purpose"] for payload in encounter_payloads] == ["follow_up"]
