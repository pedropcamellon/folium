"""Public-API end-to-end evaluation for committed chart-review benchmark cases."""

import argparse
import asyncio
import json
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Any

import httpx
from pydantic import BaseModel

from app.evals import ChartReviewBenchmarkCase, load_benchmark_case

STOP_WORDS = frozenset({"a", "an", "and", "are", "as", "has", "is", "of", "the", "to"})
EVALUATION_TERM_EQUIVALENTS = {
    "onset": frozenset({"onset", "duration"}),
    "trigger": frozenset({"trigger", "exacerbat", "exacerbate"}),
}
EVALUATION_ENVIRONMENT_KEYS = frozenset(
    {
        "FOLIUM_EVAL_ACCESS_TOKEN",
        "FOLIUM_EVAL_USER_EMAIL",
        "FOLIUM_EVAL_USER_PASSWORD",
        "FOLIUM_EVAL_API_BASE_URL",
        "FOLIUM_EVAL_POLL_INTERVAL_SECONDS",
        "FOLIUM_EVAL_POLL_TIMEOUT_SECONDS",
    }
)


def _evaluation_environment(environment_file: Path) -> dict[str, str]:
    """Read only declared evaluator variables from a dotenv-style file."""
    if not environment_file.is_file():
        return {}

    values: dict[str, str] = {}
    for line in environment_file.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.strip().removeprefix("export ").partition("=")
        if not separator or key not in EVALUATION_ENVIRONMENT_KEYS:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


@dataclass(frozen=True)
class EvaluationSettings:
    """Explicit evaluator configuration read only from process environment."""

    api_base_url: str
    access_token: str | None
    user_email: str | None
    user_password: str | None
    poll_interval_seconds: float
    poll_timeout_seconds: float

    @classmethod
    def from_environment(cls, environment_file: Path | None = None) -> "EvaluationSettings":
        environment_file = environment_file or Path(__file__).parents[3] / ".env"
        configured_values = _evaluation_environment(environment_file)

        def value(name: str) -> str | None:
            return os.environ.get(name) or configured_values.get(name)

        access_token = value("FOLIUM_EVAL_ACCESS_TOKEN")
        user_email = value("FOLIUM_EVAL_USER_EMAIL")
        user_password = value("FOLIUM_EVAL_USER_PASSWORD")
        if not access_token and not (user_email and user_password):
            raise RuntimeError(
                "set FOLIUM_EVAL_ACCESS_TOKEN or both FOLIUM_EVAL_USER_EMAIL "
                "and FOLIUM_EVAL_USER_PASSWORD"
            )
        return cls(
            api_base_url=(value("FOLIUM_EVAL_API_BASE_URL") or "http://localhost:8000").rstrip("/"),
            access_token=access_token,
            user_email=user_email,
            user_password=user_password,
            poll_interval_seconds=float(value("FOLIUM_EVAL_POLL_INTERVAL_SECONDS") or "1"),
            poll_timeout_seconds=float(value("FOLIUM_EVAL_POLL_TIMEOUT_SECONDS") or "120"),
        )


class EvaluationResult(BaseModel):
    """Public terminal-review evidence produced for one evaluation case."""

    case_id: str
    passed: bool
    failures: list[str]
    review_status: str
    elapsed_seconds: float
    review: dict[str, Any]


class EvaluationSuiteResult(BaseModel):
    """Aggregate public terminal-review evidence for a sequential benchmark suite."""

    passed: bool
    results: list[EvaluationResult]


def benchmark_case_paths(target: Path) -> list[Path]:
    """Resolve one case file or every case in a benchmark directory."""
    if target.is_file():
        if target.name != "case.yaml":
            raise ValueError("benchmark case files must be named case.yaml")
        return [target]
    if target.is_dir():
        paths = sorted(target.glob("patient-*/case.yaml"))
        if paths:
            return paths
        raise ValueError(f"benchmark directory contains no patient-*/case.yaml files: {target}")
    raise ValueError(f"benchmark path does not exist: {target}")


def _normalized_terms(text: str) -> set[str]:
    """Return stable lexical terms for deterministic paraphrase-tolerant scoring."""
    terms = set(re.findall(r"[a-z]+", text.casefold())) - STOP_WORDS
    normalized_terms: set[str] = set()
    for term in terms:
        if term.endswith("ement"):
            normalized_terms.add(term[: -len("ement")])
        elif term.endswith("ing"):
            normalized_terms.add(term[: -len("ing")])
        elif term.endswith("ed"):
            normalized_terms.add(term[: -len("ed")])
        elif term.endswith("s"):
            normalized_terms.add(term[:-1])
        else:
            normalized_terms.add(term)
    return normalized_terms


def _preserves_missing_information(expectation: str, output_terms: set[str]) -> bool:
    """Recognize approved deterministic wording variants for declared gaps."""
    expectation_terms = _normalized_terms(expectation) - {"available", "not"}
    return _preserves_expected_terms(expectation_terms, output_terms)


def _preserves_expected_terms(expectation_terms: set[str], output_terms: set[str]) -> bool:
    """Require every expected term, allowing a small approved equivalent set."""
    return all(
        output_terms.intersection(EVALUATION_TERM_EQUIVALENTS.get(term, {term}))
        for term in expectation_terms
    )


def score_review(case: ChartReviewBenchmarkCase, review: dict[str, Any]) -> list[str]:
    """Score public terminal-review behavior available to the E2E evaluator."""
    status = review.get("status")
    if status != "completed":
        return [f"chart review finished with status: {status}"]

    output_text = "\n".join(
        [
            str(review.get("summary") or ""),
            str(review.get("reasoning") or ""),
            *(str(item) for item in review.get("missingInfo", [])),
            *(str(item) for item in review.get("followUpQuestions", [])),
        ]
    )
    output_terms = _normalized_terms(output_text)
    failures: list[str] = []
    for fact in case.expected.output.summary_facts:
        if not _preserves_expected_terms(_normalized_terms(fact), output_terms):
            failures.append(f"summary did not preserve required fact: {fact}")
    for missing_information in case.expected.output.missing_information:
        if not _preserves_missing_information(missing_information, output_terms):
            failures.append(f"missing-information item was not preserved: {missing_information}")

    return failures


async def _authenticate(client: httpx.AsyncClient, settings: EvaluationSettings) -> None:
    if settings.access_token:
        client.headers["Authorization"] = f"Bearer {settings.access_token}"
        return
    response = await client.post(
        "/auth/jwt/login",
        data={"username": settings.user_email, "password": settings.user_password},
    )
    response.raise_for_status()
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"


async def _create_patient(client: httpx.AsyncClient, case: ChartReviewBenchmarkCase) -> str:
    response = await client.post(
        "/api/v1/patients/",
        json={
            "medicalRecordNumber": f"EVAL-{case.fixture.patient.key}-{uuid.uuid4().hex[:12]}",
            "firstName": "Evaluation",
            "lastName": case.fixture.patient.key,
            "dateOfBirth": case.fixture.patient.date_of_birth.isoformat(),
            "gender": case.fixture.patient.gender,
            "contactInfo": "Evaluation-only record",
        },
    )
    response.raise_for_status()
    return response.json()["id"]


async def _create_encounters(
    client: httpx.AsyncClient, case: ChartReviewBenchmarkCase, patient_id: str
) -> str:
    active_encounter_id = ""
    for encounter in case.fixture.encounters:
        response = await client.post(
            "/api/v1/encounters/",
            json={
                "patientId": patient_id,
                "encounterType": "outpatient",
                "purpose": "follow_up",
                "status": "completed",
                "title": encounter.title,
                "startedAt": encounter.occurred_at.isoformat(),
                "summary": encounter.summary,
                "description": encounter.description,
                "createdBy": "evaluation-runner",
            },
        )
        response.raise_for_status()
        encounter_id = response.json()["id"]
        if encounter.note:
            response = await client.post(
                f"/api/v1/encounters/{encounter_id}/narratives",
                json={"encounterId": encounter_id, "content": encounter.note, "status": "final"},
            )
            response.raise_for_status()
        if encounter.key == case.fixture.active_encounter_key:
            active_encounter_id = encounter_id
    if not active_encounter_id:
        raise RuntimeError("fixture did not create an active encounter")
    return active_encounter_id


async def _poll_terminal_review(
    client: httpx.AsyncClient, encounter_id: str, settings: EvaluationSettings
) -> dict[str, Any]:
    deadline = monotonic() + settings.poll_timeout_seconds
    while monotonic() < deadline:
        response = await client.get(f"/api/v1/encounters/{encounter_id}/chart-review")
        response.raise_for_status()
        review = response.json()
        if review is not None and review["status"] in {"completed", "failed"}:
            return review
        await asyncio.sleep(settings.poll_interval_seconds)
    raise TimeoutError("chart review did not reach a terminal state before the evaluation timeout")


async def evaluate_case(
    path: Path, settings: EvaluationSettings, transport: httpx.AsyncBaseTransport | None = None
) -> EvaluationResult:
    """Exercise authenticated public APIs, Temporal, worker, and local provider for one case."""
    case = load_benchmark_case(path)
    started_at = monotonic()
    async with httpx.AsyncClient(
        base_url=settings.api_base_url,
        timeout=settings.poll_timeout_seconds,
        transport=transport,
    ) as client:
        await _authenticate(client, settings)
        patient_id = await _create_patient(client, case)
        try:
            encounter_id = await _create_encounters(client, case, patient_id)
            response = await client.post(f"/api/v1/encounters/{encounter_id}/chart-review")
            response.raise_for_status()
            review = await _poll_terminal_review(client, encounter_id, settings)
        finally:
            response = await client.delete(f"/api/v1/patients/{patient_id}")
            response.raise_for_status()

    failures = score_review(case, review)
    return EvaluationResult(
        case_id=case.id,
        passed=not failures,
        failures=failures,
        review_status=str(review["status"]),
        elapsed_seconds=round(monotonic() - started_at, 3),
        review=review,
    )


async def evaluate_suite(
    target: Path, settings: EvaluationSettings, transport: httpx.AsyncBaseTransport | None = None
) -> EvaluationSuiteResult:
    """Evaluate benchmark cases sequentially to preserve local-provider comparability."""
    results = [
        await evaluate_case(path, settings, transport) for path in benchmark_case_paths(target)
    ]
    return EvaluationSuiteResult(passed=all(result.passed for result in results), results=results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run chart-review benchmark cases end to end")
    parser.add_argument("target", type=Path, help="Path to case.yaml or a benchmark directory")
    args = parser.parse_args()
    result = asyncio.run(evaluate_suite(args.target, EvaluationSettings.from_environment()))
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    if not result.passed:
        raise SystemExit(1)
