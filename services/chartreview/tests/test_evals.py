"""Fast request-sequence coverage for chart-review evaluation cases."""

import asyncio
import os
from pathlib import Path

import httpx

from app.e2e_eval_runner import EvaluationSettings, benchmark_case_paths, evaluate_case

os.environ.setdefault("AI_SERVICE_BASE_URL", "http://localhost:8002")
os.environ.setdefault("CHARTREVIEW_BACKEND_URL", "http://localhost:8000")
os.environ.setdefault("CHARTREVIEW_INTERNAL_TOKEN", "test-token")

from folium.core.chart_review import ChartReviewInput, ChartReviewSourceChunk, ChartReviewSourceType

from app.graph import _format_active_context

CASE_PATH = (
    Path(__file__).parents[1] / "evals" / "chart_review_bench" / "v1" / "patient-001" / "case.yaml"
)
PROMPT_PATH = Path(__file__).parents[1] / "prompts" / "chart_review.md"
BENCHMARK_PATH = CASE_PATH.parents[1]


def test_benchmark_directory_resolves_committed_cases_in_order() -> None:
    assert benchmark_case_paths(BENCHMARK_PATH) == [
        BENCHMARK_PATH / "patient-001" / "case.yaml",
        BENCHMARK_PATH / "patient-002" / "case.yaml",
    ]


def test_chart_review_prompt_prioritizes_active_encounter_facts() -> None:
    prompt = PROMPT_PATH.read_text(encoding="utf-8")

    assert "active encounter context as the patient's current state" in prompt
    assert "Do not ask follow-up questions for facts already stated" in prompt
    assert "review_flags" not in prompt


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


def test_patient_001_exercises_the_public_evaluation_lifecycle(tmp_path: Path) -> None:
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
            encounter_id = "active-id" if len(requests) == 4 else "prior-id"
            return httpx.Response(201, json={"id": encounter_id})
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
                    "summary": "Cough, nasal congestion, and fever are present; cold air exacerbates coughing.",
                    "reasoning": "Symptom duration is not specified.",
                    "missingInfo": ["Duration of fever"],
                    "followUpQuestions": [
                        "When did symptoms begin?",
                        "How long has the fever been present?",
                    ],
                },
            )
        if request.url.path == "/api/v1/patients/patient-id" and request.method == "DELETE":
            return httpx.Response(204)
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    result = asyncio.run(
        evaluate_case(
            CASE_PATH,
            EvaluationSettings(
                "http://testserver", None, settings.user_email, settings.user_password, 0, 1
            ),
            transport=httpx.MockTransport(respond),
        )
    )

    assert result.passed is True
    assert [request.method for request in requests] == [
        "POST",
        "POST",
        "POST",
        "POST",
        "POST",
        "POST",
        "GET",
        "DELETE",
    ]
