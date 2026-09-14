"""Local manual-review artifact coverage."""

import csv
import json
from pathlib import Path

from app.e2e_eval_runner import (
    EvaluationAxisResult,
    EvaluationResult,
    EvaluationSuiteResult,
    write_evaluation_artifacts,
)


def test_write_evaluation_artifacts_creates_manual_review_files(tmp_path: Path) -> None:
    result = EvaluationSuiteResult(
        passed=False,
        results=[
            EvaluationResult(
                case_id="test-case",
                passed=False,
                axes=[
                    EvaluationAxisResult(name="validation", passed=True, failures=[]),
                    EvaluationAxisResult(
                        name="retrieval", passed=False, failures=["unexpected lookup"]
                    ),
                ],
                review_status="completed",
                elapsed_seconds=1.25,
                review={"status": "completed"},
            )
        ],
    )

    written_result = write_evaluation_artifacts(result, tmp_path)

    artifact_dir = Path(written_result.artifact_directory or "")
    assert json.loads((artifact_dir / "suite.json").read_text(encoding="utf-8"))["passed"] is False
    assert len((artifact_dir / "cases.jsonl").read_text(encoding="utf-8").splitlines()) == 1
    with (artifact_dir / "review_queue.csv").open(encoding="utf-8", newline="") as queue_file:
        assert list(csv.DictReader(queue_file))[0]["failed_axes"] == "retrieval"
