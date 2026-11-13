"""Deterministic routing tests for bounded chart-review history retrieval."""

import os
import pytest
from pydantic import TypeAdapter, ValidationError

os.environ.setdefault("AI_SERVICE_BASE_URL", "http://localhost:8002")
os.environ.setdefault("CHARTREVIEW_BACKEND_URL", "http://localhost:8000")
os.environ.setdefault("CHARTREVIEW_INTERNAL_TOKEN", "test-token")

from app.graph import (
    MAX_HISTORY_RETRIEVAL_ATTEMPTS,
    build_chartreview_graph,
    filter_new_history_search_terms,
    next_after_history_action,
    next_after_history_plan,
    next_after_history_retrieval,
)
from app.models import (
    ChartReviewHistoryAction,
    ChartReviewHistoryPlan,
    NoSearchPlan,
    SearchHistoryAction,
    SearchHistoryPlan,
    StopHistoryAction,
)

history_plan_adapter = TypeAdapter(ChartReviewHistoryPlan)
history_action_adapter = TypeAdapter(ChartReviewHistoryAction)


def test_history_retrieval_retries_after_empty_result_before_cap() -> None:
    state = {
        "historical_source_chunks": [],
        "history_search_terms": ["albuterol"],
        "history_retrieval_attempts": 1,
    }

    assert next_after_history_retrieval(state) == "decide_history_action"


def test_history_retrieval_stops_after_match() -> None:
    state = {
        "historical_source_chunks": [
            {"source_id": "history-interaction-summary:example"}
        ],
        "history_search_terms": ["albuterol"],
        "history_retrieval_attempts": 1,
    }

    assert next_after_history_retrieval(state) == "generate_review"


def test_history_retrieval_stops_at_attempt_cap() -> None:
    state = {
        "historical_source_chunks": [],
        "history_search_terms": ["albuterol"],
        "history_retrieval_attempts": MAX_HISTORY_RETRIEVAL_ATTEMPTS,
    }

    assert next_after_history_retrieval(state) == "generate_review"


def test_chartreview_graph_compiles_with_bounded_history_loop() -> None:
    assert build_chartreview_graph().compile() is not None


def test_search_plan_survives_graph_state_serialization() -> None:
    plan = SearchHistoryPlan(
        outcome="search_history",
        factual_gap="Missing inhaler",
        evidence_objective="Find a previously documented inhaler",
        evidence_scope="approved_prior_interactions",
        success_condition="approved_block_returned",
        stop_policy="bounded_history",
    )

    rehydrated = history_plan_adapter.validate_json(plan.model_dump_json())

    assert rehydrated == plan


def test_no_search_plan_survives_graph_state_serialization() -> None:
    plan = NoSearchPlan(
        outcome="no_search", reason="active_context_sufficient"
    )

    rehydrated = history_plan_adapter.validate_json(plan.model_dump_json())

    assert rehydrated == plan


def test_search_plan_routes_to_separate_action() -> None:
    state = {
        "history_plan": SearchHistoryPlan(
            outcome="search_history",
            factual_gap="Missing inhaler",
            evidence_objective="Find a previously documented inhaler",
            evidence_scope="approved_prior_interactions",
            success_condition="approved_block_returned",
            stop_policy="bounded_history",
        ).model_dump()
    }

    assert next_after_history_plan(state) == "decide_history_action"


def test_no_search_plan_bypasses_history_lookup() -> None:
    state = {
        "history_plan": NoSearchPlan(
            outcome="no_search", reason="active_context_sufficient"
        ).model_dump()
    }

    assert next_after_history_plan(state) == "generate_review"


def test_stop_action_bypasses_history_lookup() -> None:
    state = {
        "history_action": StopHistoryAction(
            action="stop", reason="no_new_terms"
        ).model_dump(),
        "history_search_terms": [],
    }

    assert next_after_history_action(state) == "generate_review"


def test_repeated_normalized_terms_do_not_select_another_lookup() -> None:
    new_terms = filter_new_history_search_terms(
        [" Albuterol ", "ALBUTEROL", "inhaler usage"],
        ["albuterol", "inhaler   usage"],
    )
    state = {"history_search_terms": new_terms}

    assert new_terms == []
    assert next_after_history_action(state) == "generate_review"


def test_search_action_survives_state_serialization() -> None:
    action = SearchHistoryAction(
        action="search_history", search_terms=["albuterol"]
    )

    assert history_action_adapter.validate_json(action.model_dump_json()) == action


@pytest.mark.parametrize(
    "payload",
    [
        {
            "outcome": "search_history",
            "factual_gap": " ",
            "evidence_objective": "Find a prior fact",
            "evidence_scope": "approved_prior_interactions",
            "success_condition": "approved_block_returned",
            "stop_policy": "bounded_history",
        },
        {
            "outcome": "search_history",
            "factual_gap": "Missing inhaler",
            "evidence_objective": "Find a prior fact",
            "evidence_scope": "all_documents",
            "success_condition": "approved_block_returned",
            "stop_policy": "bounded_history",
        },
        {"outcome": "no_search", "reason": "active_context_sufficient", "tool": "sql"},
    ],
)
def test_history_plan_rejects_invalid_or_unbounded_payload(payload: dict) -> None:
    with pytest.raises(ValidationError):
        history_plan_adapter.validate_python(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"action": "search_history", "search_terms": [" "]},
        {"action": "search_history", "search_terms": []},
        {"action": "search_history", "search_terms": ["x"] * 4},
        {"action": "stop", "reason": "unknown"},
        {"action": "search_history", "search_terms": ["term"], "scope": "all"},
    ],
)
def test_history_action_rejects_invalid_or_unbounded_payload(payload: dict) -> None:
    with pytest.raises(ValidationError):
        history_action_adapter.validate_python(payload)
