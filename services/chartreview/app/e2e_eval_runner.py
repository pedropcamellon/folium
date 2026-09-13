"""Public-API end-to-end evaluation for committed chart-review benchmark cases."""

import argparse
import asyncio
import csv
import hashlib
import json
import os
import re
import uuid
import warnings
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from time import monotonic
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        message='Field "model_name" in PromptModelConfig has conflict with protected namespace',
        category=UserWarning,
    )
    import mlflow

from app.evals import ChartReviewBenchmarkCase, load_benchmark_case
from app.prompts import chart_review_prompt_path

STOP_WORDS = frozenset({"a", "an", "and", "are", "as", "has", "is", "of", "the", "to"})
EVALUATION_TERM_EQUIVALENTS = {
    "onset": frozenset({"onset", "duration"}),
    "trigger": frozenset({"trigger", "exacerbat", "exacerbate"}),
    "present": frozenset({"present", "intact", "experienc"}),
    "occur": frozenset({"occur", "sustain"}),
}
EVALUATION_ENVIRONMENT_KEYS = frozenset(
    {
        "FOLIUM_EVAL_ACCESS_TOKEN",
        "FOLIUM_EVAL_USER_EMAIL",
        "FOLIUM_EVAL_USER_PASSWORD",
        "FOLIUM_EVAL_API_BASE_URL",
        "FOLIUM_EVAL_POLL_INTERVAL_SECONDS",
        "FOLIUM_EVAL_POLL_TIMEOUT_SECONDS",
        "FOLIUM_EVAL_INTERNAL_TOKEN",
        "FOLIUM_EVAL_EVALUATION_TOKEN",
        "FOLIUM_EVAL_ARTIFACTS_DIR",
        "FOLIUM_EVAL_MLFLOW_EXPERIMENT_NAME",
        "FOLIUM_EVAL_MODEL_NAME",
        "FOLIUM_EVAL_PROMPT_VERSION",
        "FOLIUM_EVAL_DATASET_VERSION",
        "FOLIUM_EVAL_RUN_LABEL",
        "MLFLOW_TRACKING_URI",
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
    artifacts_dir: Path
    internal_token: str | None = None
    evaluation_token: str | None = None
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "chart-review-evaluations-v1"
    model_name: str = "unknown"
    prompt_version: str | None = None
    dataset_version: str | None = None
    run_label: str | None = None

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
            poll_timeout_seconds=float(value("FOLIUM_EVAL_POLL_TIMEOUT_SECONDS") or "600"),
            artifacts_dir=Path(
                value("FOLIUM_EVAL_ARTIFACTS_DIR")
                or Path(__file__).parents[3] / "artifacts/evaluations/chart-review"
            ),
            internal_token=value("FOLIUM_EVAL_INTERNAL_TOKEN"),
            evaluation_token=value("FOLIUM_EVAL_EVALUATION_TOKEN"),
            mlflow_tracking_uri=value("MLFLOW_TRACKING_URI") or "http://localhost:5000",
            mlflow_experiment_name=value("FOLIUM_EVAL_MLFLOW_EXPERIMENT_NAME")
            or "chart-review-evaluations-v1",
            model_name=value("FOLIUM_EVAL_MODEL_NAME")
            or os.environ.get("AI_MODEL_NAME", "unknown"),
            prompt_version=value("FOLIUM_EVAL_PROMPT_VERSION"),
            dataset_version=value("FOLIUM_EVAL_DATASET_VERSION"),
            run_label=value("FOLIUM_EVAL_RUN_LABEL"),
        )


class EvaluationAxisResult(BaseModel):
    """One independently scored chart-review quality dimension."""

    name: str
    passed: bool
    failures: list[str]


class EvaluationResult(BaseModel):
    """Public terminal-review evidence produced for one evaluation case."""

    case_id: str
    passed: bool
    axes: list[EvaluationAxisResult]
    review_status: str
    elapsed_seconds: float
    stage_durations_seconds: dict[str, float] = Field(default_factory=dict)
    review: dict[str, Any]


class EvaluationSuiteResult(BaseModel):
    """Aggregate public terminal-review evidence for a sequential benchmark suite."""

    passed: bool
    results: list[EvaluationResult]
    artifact_directory: str | None = None


class EvaluationTrackingMetadata(BaseModel):
    """Stable versions and identity tags for one comparable benchmark run."""

    model_config = ConfigDict(protected_namespaces=())

    dataset_version: str
    prompt_version: str
    model_name: str
    rubric_version: str = "chart-review-axes-v1"
    gate_policy_version: str = "all-axes-pass-v1"
    run_label: str | None = None


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


def score_review_axes(
    case: ChartReviewBenchmarkCase,
    review: dict[str, Any],
    encounter_ids: dict[str, str],
    cited_source_ids: list[str] | None,
) -> list[EvaluationAxisResult]:
    """Score independently actionable validation, draft, and retrieval evidence."""
    status = review.get("status")
    expected_status = (
        "completed" if case.expected.validation.expected_status == "valid" else "failed"
    )
    if status != expected_status:
        return [
            EvaluationAxisResult(
                name="validation",
                passed=False,
                failures=[
                    f"chart review finished with status: {status}; expected {expected_status}"
                ],
            )
        ]
    if status == "failed":
        return [EvaluationAxisResult(name="validation", passed=True, failures=[])]

    draft_failures: list[str] = []
    output_text = "\n".join(
        [
            str(review.get("summary") or ""),
            str(review.get("reasoning") or ""),
            *(str(item) for item in review.get("missingInfo", [])),
            *(str(item) for item in review.get("followUpQuestions", [])),
        ]
    )
    output_terms = _normalized_terms(output_text)
    for fact in case.expected.output.summary_facts:
        if not _preserves_expected_terms(_normalized_terms(fact), output_terms):
            draft_failures.append(f"summary did not preserve required fact: {fact}")
    for missing_information in case.expected.output.missing_information:
        if not _preserves_missing_information(missing_information, output_terms):
            draft_failures.append(
                f"missing-information item was not preserved: {missing_information}"
            )
    for claim in case.expected.output.forbidden_claims:
        if _preserves_expected_terms(_normalized_terms(claim), output_terms):
            draft_failures.append(f"draft included forbidden claim: {claim}")

    follow_up_questions = review.get("followUpQuestions", [])
    if not case.expected.output.follow_up_questions and follow_up_questions:
        draft_failures.append("follow-up questions were returned when none were expected")
    follow_up_terms = _normalized_terms(
        "\n".join(str(question) for question in follow_up_questions)
    )
    for term in case.expected.output.required_follow_up_terms:
        if not _preserves_expected_terms(_normalized_terms(term), follow_up_terms):
            draft_failures.append(f"follow-up questions omitted required term: {term}")
    for term in case.expected.output.forbidden_follow_up_terms:
        if _preserves_expected_terms(_normalized_terms(term), follow_up_terms):
            draft_failures.append(f"follow-up questions included forbidden term: {term}")

    retrieval_failures: list[str] = []
    history_search_terms = [
        str(search_term)
        for search_term in review.get("historySearchTerms", [])
        if isinstance(search_term, str)
    ]
    history_results = review.get("historyResults", [])
    if not case.expected.history_decision.should_retrieve:
        if history_search_terms:
            retrieval_failures.append("history retrieval was requested when no lookup was expected")
        if history_results:
            retrieval_failures.append(
                "history retrieval returned blocks when no lookup was expected"
            )
    for source_role in case.expected.history_decision.expected_returned_source_roles:
        if not _returned_history_matches_source_role(case, source_role, history_results):
            retrieval_failures.append(
                f"history retrieval did not return expected source role: {source_role}"
            )
    for term in case.expected.history_decision.forbidden_search_terms:
        if any(
            _preserves_expected_terms(_normalized_terms(term), _normalized_terms(search_term))
            for search_term in history_search_terms
        ):
            retrieval_failures.append(f"history retrieval included forbidden search term: {term}")

    provenance_failures: list[str] = []
    if cited_source_ids is None:
        provenance_failures.append("canonical citation evidence was unavailable")
    else:
        required_source_ids = [
            _canonical_source_id(case, source_role, encounter_ids)
            for source_role in case.expected.output.required_source_roles
        ]
        forbidden_source_ids = [
            _canonical_source_id(case, source_role, encounter_ids)
            for source_role in case.expected.output.forbidden_source_roles
        ]
        for source_id in required_source_ids:
            if source_id not in cited_source_ids:
                provenance_failures.append(f"required source was not cited: {source_id}")
        for source_id in forbidden_source_ids:
            if source_id in cited_source_ids:
                provenance_failures.append(f"forbidden source was cited: {source_id}")

    return [
        EvaluationAxisResult(name="validation", passed=True, failures=[]),
        EvaluationAxisResult(name="draft", passed=not draft_failures, failures=draft_failures),
        EvaluationAxisResult(
            name="retrieval", passed=not retrieval_failures, failures=retrieval_failures
        ),
        EvaluationAxisResult(
            name="provenance", passed=not provenance_failures, failures=provenance_failures
        ),
    ]


def _canonical_source_id(
    case: ChartReviewBenchmarkCase, source_role: str, encounter_ids: dict[str, str]
) -> str:
    """Resolve a fixture source role to the canonical ID supplied to the provider."""
    encounter_key, content_role = source_role.rsplit(".", maxsplit=1)
    if encounter_key == "active":
        encounter_key = case.fixture.active_encounter_key
    encounter_id = encounter_ids[encounter_key]
    if content_role == "note":
        return f"encounter-note:{encounter_id}"
    source_id = f"encounter-{content_role.replace(' ', '-')}:{encounter_id}"
    return (
        source_id if encounter_key == case.fixture.active_encounter_key else f"history-{source_id}"
    )


def _returned_history_matches_source_role(
    case: ChartReviewBenchmarkCase, source_role: str, history_results: object
) -> bool:
    """Match public history metadata to the fixture source expected by one case."""
    encounter_key, content_role = source_role.rsplit(".", maxsplit=1)
    encounter = next(
        encounter for encounter in case.fixture.encounters if encounter.key == encounter_key
    )
    expected_content = getattr(encounter, content_role)
    expected_content_role = "voice-note transcript" if content_role == "note" else content_role
    return isinstance(history_results, list) and any(
        isinstance(result, dict)
        and result.get("displayLabel") == encounter.title
        and result.get("contentRole") == expected_content_role
        and result.get("content") == expected_content
        for result in history_results
    )


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
) -> tuple[str, dict[str, str]]:
    active_encounter_id = ""
    encounter_ids: dict[str, str] = {}
    for encounter in case.fixture.encounters:
        response = await client.post(
            "/api/v1/encounters/",
            json={
                "patientId": patient_id,
                "encounterType": "outpatient",
                "purpose": encounter.purpose,
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
        encounter_ids[encounter.key] = encounter_id
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
    return active_encounter_id, encounter_ids


async def _get_evaluation_evidence(
    client: httpx.AsyncClient, review_id: str, settings: EvaluationSettings
) -> dict[str, Any] | None:
    """Fetch canonical citations only when explicit evaluator credentials are configured."""
    if not settings.internal_token or not settings.evaluation_token:
        return None
    response = await client.get(
        f"/api/v1/encounters/internal/chart-review/{review_id}/evaluation-evidence",
        headers={
            "X-ChartReview-Internal-Token": settings.internal_token,
            "X-ChartReview-Evaluation-Token": settings.evaluation_token,
        },
    )
    response.raise_for_status()
    return response.json()


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
    stage_started_at = started_at
    stage_durations_seconds: dict[str, float] = {}
    async with httpx.AsyncClient(
        base_url=settings.api_base_url,
        timeout=settings.poll_timeout_seconds,
        transport=transport,
    ) as client:
        await _authenticate(client, settings)
        stage_started_at = monotonic()
        patient_id = await _create_patient(client, case)
        try:
            encounter_id, encounter_ids = await _create_encounters(client, case, patient_id)
            stage_durations_seconds["seeding"] = round(monotonic() - stage_started_at, 3)
            stage_started_at = monotonic()
            response = await client.post(f"/api/v1/encounters/{encounter_id}/chart-review")
            response.raise_for_status()
            review = await _poll_terminal_review(client, encounter_id, settings)
            stage_durations_seconds["review"] = round(monotonic() - stage_started_at, 3)
            stage_started_at = monotonic()
            evidence = await _get_evaluation_evidence(client, str(review["id"]), settings)
            stage_durations_seconds["evidence"] = round(monotonic() - stage_started_at, 3)
        finally:
            response = await client.delete(f"/api/v1/patients/{patient_id}")
            response.raise_for_status()

    axes = score_review_axes(
        case,
        review,
        encounter_ids,
        list(evidence.get("citedSourceIds", [])) if evidence is not None else None,
    )
    stage_durations_seconds["scoring"] = round(monotonic() - stage_started_at, 3)
    return EvaluationResult(
        case_id=case.id,
        passed=all(axis.passed for axis in axes),
        axes=axes,
        review_status=str(review["status"]),
        elapsed_seconds=round(monotonic() - started_at, 3),
        stage_durations_seconds=stage_durations_seconds,
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


def write_evaluation_artifacts(
    result: EvaluationSuiteResult, artifacts_dir: Path
) -> EvaluationSuiteResult:
    """Write ignored local evidence for manual review and future MLflow import."""
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + f"-{uuid.uuid4().hex[:8]}"
    run_dir = artifacts_dir / run_id
    run_dir.mkdir(parents=True)
    completed_result = result.model_copy(update={"artifact_directory": str(run_dir)})
    (run_dir / "suite.json").write_text(
        json.dumps(completed_result.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )
    with (run_dir / "cases.jsonl").open("w", encoding="utf-8") as artifact_file:
        for case_result in completed_result.results:
            artifact_file.write(json.dumps(case_result.model_dump(mode="json")) + "\n")
    with (run_dir / "review_queue.csv").open("w", encoding="utf-8", newline="") as queue_file:
        writer = csv.DictWriter(
            queue_file,
            fieldnames=["case_id", "passed", "review_status", "elapsed_seconds", "failed_axes"],
        )
        writer.writeheader()
        for case_result in completed_result.results:
            writer.writerow(
                {
                    "case_id": case_result.case_id,
                    "passed": case_result.passed,
                    "review_status": case_result.review_status,
                    "elapsed_seconds": case_result.elapsed_seconds,
                    "failed_axes": ",".join(
                        axis.name for axis in case_result.axes if not axis.passed
                    ),
                }
            )
    return completed_result


def _prompt_fingerprint(prompt_version: str) -> str:
    prompt_path = chart_review_prompt_path(prompt_version)
    return f"{prompt_version}:sha256:{hashlib.sha256(prompt_path.read_bytes()).hexdigest()[:12]}"


def tracking_metadata(target: Path, settings: EvaluationSettings) -> EvaluationTrackingMetadata:
    """Derive comparable run tags from committed benchmark and prompt inputs."""
    cases = [load_benchmark_case(path) for path in benchmark_case_paths(target)]
    evaluation_packs = {case.metadata.evaluation_pack for case in cases}
    if len(evaluation_packs) != 1:
        raise ValueError("a tracked evaluation suite must contain one evaluation pack")
    return EvaluationTrackingMetadata(
        dataset_version=settings.dataset_version or evaluation_packs.pop(),
        prompt_version=_prompt_fingerprint(settings.prompt_version or "v1"),
        model_name=settings.model_name,
        run_label=settings.run_label,
    )


def _percentile_95(values: list[float]) -> float:
    return sorted(values)[max(0, (len(values) * 95 + 99) // 100 - 1)]


def aggregate_metrics(result: EvaluationSuiteResult) -> dict[str, float]:
    """Produce deterministic aggregate metrics without including review content."""
    elapsed_seconds = [case_result.elapsed_seconds for case_result in result.results]
    metrics = {
        "case_count": float(len(result.results)),
        "pass_rate": sum(case_result.passed for case_result in result.results)
        / len(result.results),
        "elapsed_seconds_min": min(elapsed_seconds),
        "elapsed_seconds_median": median(elapsed_seconds),
        "elapsed_seconds_p95": _percentile_95(elapsed_seconds),
        "elapsed_seconds_max": max(elapsed_seconds),
        "validation_failure_count": float(
            sum(
                not axis.passed
                for case_result in result.results
                for axis in case_result.axes
                if axis.name == "validation"
            )
        ),
    }
    axis_names = {axis.name for case_result in result.results for axis in case_result.axes}
    for axis_name in axis_names:
        metrics[f"{axis_name}_pass_rate"] = sum(
            axis.passed
            for case_result in result.results
            for axis in case_result.axes
            if axis.name == axis_name
        ) / len(result.results)
    stage_names = {
        stage_name
        for case_result in result.results
        for stage_name in case_result.stage_durations_seconds
    }
    for stage_name in stage_names:
        durations = [
            case_result.stage_durations_seconds[stage_name]
            for case_result in result.results
            if stage_name in case_result.stage_durations_seconds
        ]
        metrics[f"{stage_name}_seconds_median"] = median(durations)
        metrics[f"{stage_name}_seconds_p95"] = _percentile_95(durations)
    return metrics


def track_evaluation_run(
    result: EvaluationSuiteResult,
    metadata: EvaluationTrackingMetadata,
    settings: EvaluationSettings,
    tracking_client: Any = mlflow,
) -> None:
    """Log aggregate evidence and a safe review queue to local MLflow."""
    if not result.artifact_directory:
        raise ValueError("write local evaluation artifacts before MLflow tracking")
    artifact_directory = Path(result.artifact_directory)
    safe_summary = {
        "passed": result.passed,
        "metrics": aggregate_metrics(result),
        "cases": [
            {
                "case_id": case_result.case_id,
                "passed": case_result.passed,
                "review_status": case_result.review_status,
                "elapsed_seconds": case_result.elapsed_seconds,
                "failed_axes": [axis.name for axis in case_result.axes if not axis.passed],
            }
            for case_result in result.results
        ],
    }
    tracking_client.set_tracking_uri(settings.mlflow_tracking_uri)
    tracking_client.set_experiment(settings.mlflow_experiment_name)
    with tracking_client.start_run(run_name=metadata.run_label):
        tracking_client.set_tags(metadata.model_dump(exclude_none=True))
        tracking_client.log_params(
            {
                "case_count": len(result.results),
                "runner": "chartreview-eval",
                "execution_path": "public-api-temporal",
            }
        )
        tracking_client.log_metrics(aggregate_metrics(result))
        tracking_client.log_artifact(str(artifact_directory / "review_queue.csv"))
        tracking_client.log_text(json.dumps(safe_summary, indent=2) + "\n", "summary.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run chart-review benchmark cases end to end")
    parser.add_argument("target", type=Path, help="Path to case.yaml or a benchmark directory")
    args = parser.parse_args()
    settings = EvaluationSettings.from_environment()
    result = asyncio.run(evaluate_suite(args.target, settings))
    result = write_evaluation_artifacts(result, settings.artifacts_dir)
    track_evaluation_run(result, tracking_metadata(args.target, settings), settings)
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    if not result.passed:
        raise SystemExit(1)
