"""Deterministic chart-review evaluation scoring coverage."""

from app.e2e_eval_runner import score_review_axes
from app.evals import ChartReviewBenchmarkCase


def _case(
    *,
    should_retrieve: bool = False,
    forbidden_search_terms: list[str] | None = None,
    expected_returned_source_roles: list[str] | None = None,
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
                        "key": "prior",
                        "occurred_at": "2025-01-01T10:00:00Z",
                        "title": "Synthetic prior encounter",
                        "note": "Required historical fact.",
                    },
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
                    "follow_up_questions": [],
                    "forbidden_claims": ["Medication dose was increased."],
                    "required_source_roles": ["active.note"],
                },
                "history_decision": {
                    "should_retrieve": should_retrieve,
                    "forbidden_search_terms": forbidden_search_terms or [],
                    "expected_returned_source_roles": expected_returned_source_roles or [],
                },
                "validation": {"expected_status": "valid"},
            },
        }
    )


def test_score_review_rejects_unexpected_history_lookup() -> None:
    axes = score_review_axes(
        _case(forbidden_search_terms=["unnecessary"]),
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "historySearchTerms": ["unnecessary"],
            "historyResults": [],
        },
        {"active": "active-id"},
        ["encounter-note:active-id"],
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
            "historySearchTerms": ["unnecessary"],
            "historyResults": [],
        },
        {"active": "active-id"},
        ["encounter-note:active-id"],
    )

    assert [(axis.name, axis.passed) for axis in axes] == [
        ("validation", True),
        ("draft", True),
        ("retrieval", False),
        ("provenance", True),
    ]


def test_score_review_allows_a_history_lookup_with_no_expected_match() -> None:
    axes = score_review_axes(
        _case(should_retrieve=True),
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "historySearchTerms": ["required"],
            "historyResults": [],
        },
        {"active": "active-id"},
        ["encounter-note:active-id"],
    )

    assert next(axis for axis in axes if axis.name == "retrieval").passed is True


def test_score_review_accepts_a_returned_prior_note() -> None:
    axes = score_review_axes(
        _case(should_retrieve=True, expected_returned_source_roles=["prior.note"]),
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "historyResults": [
                {
                    "displayLabel": "Synthetic prior encounter",
                    "contentRole": "voice-note transcript",
                    "content": "Required historical fact.",
                }
            ],
        },
        {"active": "active-id", "prior": "prior-id"},
        ["encounter-note:active-id"],
    )

    assert next(axis for axis in axes if axis.name == "retrieval").passed is True


def test_score_review_rejects_questions_for_complete_context() -> None:
    axes = score_review_axes(
        _case(),
        {
            "status": "completed",
            "summary": "Required summary fact.",
            "followUpQuestions": ["Can you provide another fact?"],
        },
        {"active": "active-id"},
        ["encounter-note:active-id"],
    )

    assert next(axis for axis in axes if axis.name == "draft").failures == [
        "follow-up questions were returned when none were expected"
    ]


def test_score_review_rejects_a_fixture_forbidden_claim() -> None:
    axes = score_review_axes(
        _case(),
        {
            "status": "completed",
            "summary": "Required summary fact. Medication dose was increased.",
        },
        {"active": "active-id", "prior": "prior-id"},
        ["encounter-note:active-id"],
    )

    assert next(axis for axis in axes if axis.name == "draft").failures == [
        "draft included forbidden claim: Medication dose was increased."
    ]


def test_score_review_rejects_a_missing_required_citation() -> None:
    axes = score_review_axes(
        _case(),
        {"status": "completed", "summary": "Required summary fact."},
        {"active": "active-id"},
        [],
    )

    assert next(axis for axis in axes if axis.name == "provenance").failures == [
        "required source was not cited: encounter-note:active-id"
    ]


def test_score_review_rejects_an_unexpected_terminal_status() -> None:
    axes = score_review_axes(
        _case(),
        {"status": "failed"},
        {"active": "active-id"},
        [],
    )

    assert axes[0].failures == [
        "chart review finished with status: failed; expected completed"
    ]
