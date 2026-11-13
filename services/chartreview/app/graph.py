"""Bounded LangGraph definition for one chart-review draft."""

import json
import logging
from datetime import timedelta
from pathlib import Path

import httpx
from folium.ai import load_prompt, parse_chat_completion, system_message, user_message
from folium.ai.messages import OpenAIChatMessage
from folium.core.chart_review import (
    ChartReviewConfidence,
    ChartReviewHistoryRequest,
    ChartReviewHistoryResponse,
    ChartReviewInput,
    ChartReviewOutput,
    ChartReviewSourceChunk,
)
from langgraph.graph import END, START, StateGraph
from pydantic import TypeAdapter
from temporalio.common import RetryPolicy

from app.config import settings
from app.models import (
    ChartReviewGraphState,
    ChartReviewHistoryAction,
    ChartReviewHistoryPlan,
    NoSearchPlan,
    SearchHistoryAction,
    SearchHistoryPlan,
    StopHistoryAction,
)

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
CHART_REVIEW_PROMPT_PATH = PROMPTS_DIR / "chart_review.md"
CHART_REVIEW_HISTORY_PLAN_PROMPT_PATH = PROMPTS_DIR / "chart_review_history_plan.md"
CHART_REVIEW_HISTORY_ACTION_PROMPT_PATH = (
    PROMPTS_DIR / "chart_review_history_action.md"
)
MAX_HISTORY_RETRIEVAL_ATTEMPTS = 3
history_plan_adapter = TypeAdapter(ChartReviewHistoryPlan)
history_action_adapter = TypeAdapter(ChartReviewHistoryAction)


async def plan_history(state: ChartReviewGraphState) -> dict[str, ChartReviewHistoryPlan]:
    """Temporal Activity that defines the evidence objective before action selection."""
    review_input = ChartReviewInput.model_validate(state["review_input"])
    active_context = "\n\n".join(
        f"[{source.source_id}] {source.source_type.value}: {source.content}"
        for source in review_input.source_chunks
    )
    messages = [
        system_message(load_prompt(CHART_REVIEW_HISTORY_PLAN_PROMPT_PATH)),
        user_message(f"Active interaction context:\n{active_context}"),
    ]
    content = await request_model_json(messages)
    plan = history_plan_adapter.validate_json(content)
    logger.info("Chart-review history plan accepted: %s", plan)
    return {"history_plan": plan}


async def decide_history_action(
    state: ChartReviewGraphState,
) -> dict[str, ChartReviewHistoryAction | list[str]]:
    """Temporal Activity that selects bounded lexical terms for the fixed plan."""
    plan = history_plan_adapter.validate_python(state["history_plan"])
    if isinstance(plan, NoSearchPlan):
        raise ValueError("A no-search plan cannot select a history action")
    review_input = ChartReviewInput.model_validate(state["review_input"])
    active_context = "\n\n".join(
        f"[{source.source_id}] {source.source_type.value}: {source.content}"
        for source in review_input.source_chunks
    )
    messages = [
        system_message(load_prompt(CHART_REVIEW_HISTORY_ACTION_PROMPT_PATH)),
        user_message(
            f"Accepted plan:\n{plan.model_dump_json()}\n\n"
            f"Active interaction context:\n{active_context}\n\n"
            "Previously unsuccessful search terms: "
            f"{json.dumps(state.get('failed_history_search_terms', []))}"
        ),
    ]
    content = await request_model_json(messages)
    action = history_action_adapter.validate_json(content)
    if not isinstance(action, SearchHistoryAction):
        if not isinstance(action, StopHistoryAction):
            raise ValueError("Invalid chart-review history action")
        logger.info("Chart-review history action stopped: %s", action.reason)
        return {"history_action": action, "history_search_terms": []}
    search_terms = filter_new_history_search_terms(
        action.search_terms, state.get("failed_history_search_terms", [])
    )
    if not search_terms:
        logger.info(
            "Chart-review history action had no new terms; stopping search"
        )
        return {"history_search_terms": []}
    logger.info(
        "Chart-review history action selected search_terms=%s",
        search_terms,
    )
    return {
        "history_action": action,
        "history_search_terms": search_terms,
    }


def filter_new_history_search_terms(
    search_terms: list[str], failed_terms: list[str]
) -> list[str]:
    """Drop normalized duplicates while preserving terms for backend matching."""
    seen_terms = {" ".join(term.split()).casefold() for term in failed_terms}
    new_terms = []
    for term in search_terms:
        normalized_term = " ".join(term.split()).casefold()
        if normalized_term not in seen_terms:
            new_terms.append(term)
            seen_terms.add(normalized_term)
    return new_terms


async def request_model_json(messages: list[OpenAIChatMessage]) -> str:
    """Request a structured decision from the configured inference service."""
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.post(
            f"{settings.ai_service_base_url}/v1/chat/completions",
            json={
                "model": settings.ai_model_name,
                "messages": messages,
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
    return parse_chat_completion(response.json()).content


async def retrieve_history(
    state: ChartReviewGraphState,
) -> dict[str, int | list[str] | list[ChartReviewSourceChunk]]:
    """Temporal Activity that calls the backend's bounded history tool once."""
    review_input = ChartReviewInput.model_validate(state["review_input"])
    plan = history_plan_adapter.validate_python(state["history_plan"])
    if not isinstance(plan, SearchHistoryPlan):
        raise ValueError("Chart-review history lookup requires an approved search plan")
    search_terms = state.get("history_search_terms", [])
    if not search_terms:
        return {"historical_source_chunks": []}
    if state.get("history_retrieval_attempts", 0) >= MAX_HISTORY_RETRIEVAL_ATTEMPTS:
        raise ValueError("Chart-review history retrieval attempt limit exceeded")
    request = ChartReviewHistoryRequest(
        patient_id=review_input.patient_id,
        interaction_id=review_input.interaction_id,
        search_terms=search_terms,
    )
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.post(
            f"{settings.chartreview_backend_url}/api/v1/interactions/internal/chart-review/history",
            headers={
                "X-ChartReview-Internal-Token": settings.chartreview_internal_token
            },
            json=request.model_dump(mode="json"),
        )
        response.raise_for_status()
    history = ChartReviewHistoryResponse.model_validate(response.json())
    if any(
        chunk.resource_id == review_input.interaction_id
        for chunk in history.source_chunks
    ):
        raise ValueError(
            "Chart-review history retrieval returned the active interaction"
        )
    attempts = state.get("history_retrieval_attempts", 0) + 1
    logger.info(
        "Retrieved %d bounded prior chart-review source blocks",
        len(history.source_chunks),
    )
    if history.source_chunks:
        return {
            "historical_source_chunks": history.source_chunks,
            "history_retrieval_attempts": attempts,
        }
    return {
        "historical_source_chunks": [],
        "history_retrieval_attempts": attempts,
        "failed_history_search_terms": [
            *state.get("failed_history_search_terms", []),
            *search_terms,
        ],
    }


def next_after_history_plan(state: ChartReviewGraphState) -> str:
    """Skip lookup for a no-search plan; otherwise choose a separate search action."""
    plan = history_plan_adapter.validate_python(state["history_plan"])
    if isinstance(plan, NoSearchPlan):
        return "generate_review"
    return "decide_history_action"


def next_after_history_action(state: ChartReviewGraphState) -> str:
    """Only call the backend when the validated action contains new search terms."""
    if state.get("history_search_terms"):
        return "retrieve_history"
    return "generate_review"


def next_after_history_retrieval(state: ChartReviewGraphState) -> str:
    """Retry only bounded no-match searches for the accepted plan."""
    if state.get("historical_source_chunks"):
        return "generate_review"
    if (
        state.get("history_search_terms")
        and state.get("history_retrieval_attempts", 0) < MAX_HISTORY_RETRIEVAL_ATTEMPTS
    ):
        return "decide_history_action"
    return "generate_review"


async def generate_review(state: ChartReviewGraphState) -> dict[str, ChartReviewOutput]:
    """Temporal Activity that calls the provider with approved chart-review context."""
    review_input = ChartReviewInput.model_validate(state["review_input"])
    active_context = "\n\n".join(
        f"[{source.source_id}] {source.source_type.value}: {source.content}"
        for source in review_input.source_chunks
    )
    historical_source_chunks = [
        ChartReviewSourceChunk.model_validate(source)
        for source in state.get("historical_source_chunks", [])
    ]
    historical_context = "\n\n".join(
        f"[{source.source_id}] {source.source_type.value}: {source.content}"
        for source in historical_source_chunks
    )
    allowed_source_ids = [
        *(source.source_id for source in review_input.source_chunks),
        *(source.source_id for source in historical_source_chunks),
    ]
    messages = [
        system_message(load_prompt(CHART_REVIEW_PROMPT_PATH)),
        user_message(
            f"Allowed source IDs: {json.dumps(allowed_source_ids)}\n\n"
            f"Active interaction context:\n{active_context}\n\n"
            f"Approved prior interaction context:\n{historical_context or 'None supplied.'}"
        ),
    ]
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.post(
            f"{settings.ai_service_base_url}/v1/chat/completions",
            json={
                "model": settings.ai_model_name,
                "messages": messages,
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        completion = parse_chat_completion(response.json())
        content = completion.content
    logger.info("MediPhi raw chart-review completion: %s", content)
    try:
        raw_output = json.loads(content)
        normalized_output = _normalize_output(raw_output)
        normalized_output["provider_name"] = settings.ai_provider_name
        review_output = ChartReviewOutput.model_validate(normalized_output)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error(
            "MediPhi invalid chart-review completion: raw=%s error=%s", content, exc
        )
        raise

    logger.info(
        "MediPhi chart-review response validated: cited_sources=%d confidence=%s",
        len(review_output.source_refs),
        review_output.confidence,
    )
    valid_source_ids = set(allowed_source_ids)
    if any(
        source.source_id not in valid_source_ids for source in review_output.source_refs
    ):
        logger.error(
            "MediPhi cited unknown source: raw=%s allowed_source_ids=%s",
            raw_output,
            allowed_source_ids,
        )
        raise ValueError(
            "MediPhi returned a source reference outside the supplied snapshot"
        )
    return {"review_output": review_output}


def _normalize_output(output: dict) -> dict:
    """Normalize bounded local-model JSON variations before strict contract validation."""
    source_refs = output.get("source_refs")
    if isinstance(source_refs, list):
        output["source_refs"] = [
            _normalize_source_ref(source_ref) for source_ref in source_refs
        ]

    confidence = output.get("confidence")
    if isinstance(confidence, str):
        confidence_level, separator, confidence_explanation = confidence.partition("-")
        normalized_confidence = confidence_level.strip().lower()
        if normalized_confidence in {level.value for level in ChartReviewConfidence}:
            output["confidence"] = normalized_confidence
            if (
                separator
                and confidence_explanation.strip()
                and not output.get("reasoning")
            ):
                output["reasoning"] = confidence_explanation.strip()

    return output


def _normalize_source_ref(source_ref: object) -> object:
    """Accept known local-provider citation variants before strict validation."""
    if isinstance(source_ref, str):
        return {"source_id": source_ref}
    if (
        isinstance(source_ref, dict)
        and len(source_ref) == 1
        and next(iter(source_ref.values())) is True
    ):
        return {"source_id": next(iter(source_ref))}
    return source_ref


def build_chartreview_graph() -> StateGraph:
    graph = StateGraph(ChartReviewGraphState)
    graph.add_node(
        "plan_history",
        plan_history,
        metadata={
            "execute_in": "activity",
            "start_to_close_timeout": timedelta(
                seconds=settings.activity_start_to_close_timeout_seconds
            ),
            "retry_policy": RetryPolicy(
                maximum_attempts=settings.activity_max_attempts
            ),
        },
    )
    graph.add_node(
        "decide_history_action",
        decide_history_action,
        metadata={
            "execute_in": "activity",
            "start_to_close_timeout": timedelta(
                seconds=settings.activity_start_to_close_timeout_seconds
            ),
            "retry_policy": RetryPolicy(
                maximum_attempts=settings.activity_max_attempts
            ),
        },
    )
    graph.add_node(
        "retrieve_history",
        retrieve_history,
        metadata={
            "execute_in": "activity",
            "start_to_close_timeout": timedelta(
                seconds=settings.activity_start_to_close_timeout_seconds
            ),
            "retry_policy": RetryPolicy(
                maximum_attempts=settings.activity_max_attempts
            ),
        },
    )
    graph.add_node(
        "generate_review",
        generate_review,
        metadata={
            "execute_in": "activity",
            "start_to_close_timeout": timedelta(
                seconds=settings.activity_start_to_close_timeout_seconds
            ),
            "retry_policy": RetryPolicy(
                maximum_attempts=settings.activity_max_attempts
            ),
        },
    )
    graph.add_edge(START, "plan_history")
    graph.add_conditional_edges(
        "plan_history",
        next_after_history_plan,
        {
            "decide_history_action": "decide_history_action",
            "generate_review": "generate_review",
        },
    )
    graph.add_conditional_edges(
        "decide_history_action",
        next_after_history_action,
        {
            "retrieve_history": "retrieve_history",
            "generate_review": "generate_review",
        },
    )
    graph.add_conditional_edges(
        "retrieve_history",
        next_after_history_retrieval,
        {
            "decide_history_action": "decide_history_action",
            "generate_review": "generate_review",
        },
    )
    graph.add_edge("generate_review", END)
    return graph
