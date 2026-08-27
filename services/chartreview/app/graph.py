"""Bounded LangGraph definition for one chart-review draft."""

import json
import logging
from datetime import timedelta

import httpx
from folium.core.chart_review import ChartReviewInput, ChartReviewOutput
from langgraph.graph import END, START, StateGraph
from temporalio.common import RetryPolicy

from app.config import settings
from app.models import ChartReviewGraphState

logger = logging.getLogger(__name__)


async def generate_review(state: ChartReviewGraphState) -> dict[str, ChartReviewOutput]:
    """Call the local model with only the backend-curated active interaction snapshot."""
    review_input = ChartReviewInput.model_validate(state["review_input"])
    context = "\n\n".join(
        f"[{source.source_id}] {source.source_type.value}: {source.content}"
        for source in review_input.source_chunks
    )
    allowed_source_ids = [source.source_id for source in review_input.source_chunks]
    messages = [
        {
            "role": "system",
            "content": (
                "You provide draft support for clinicians. Do not diagnose, recommend treatment, "
                "or invent facts. Return JSON with summary, missing_info, follow_up_questions, "
                "source_refs, confidence, reasoning, and review_flags. Confidence must be a number "
                "from 0 to 1; do not include an explanation in the confidence field. Put evidence "
                "rationale in reasoning. Each source_refs entry "
                "must be an object with a source_id copied exactly from the allowed list. "
                "Do not return a raw interaction UUID or create a new ID."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Allowed source IDs: {json.dumps(allowed_source_ids)}\n\n"
                f"Active interaction context:\n{context}"
            ),
        },
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
        content = response.json()["choices"][0]["message"]["content"]
    logger.info("MediPhi raw chart-review completion: %s", content)
    try:
        raw_output = json.loads(content)
        normalized_output = _normalize_output(raw_output)
        normalized_output["provider_name"] = settings.ai_provider_name
        review_output = ChartReviewOutput.model_validate(normalized_output)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("MediPhi invalid chart-review completion: raw=%s error=%s", content, exc)
        raise

    logger.info(
        "MediPhi chart-review response validated: cited_sources=%d confidence=%s",
        len(review_output.source_refs),
        review_output.confidence,
    )
    valid_source_ids = set(allowed_source_ids)
    if any(source.source_id not in valid_source_ids for source in review_output.source_refs):
        logger.error(
            "MediPhi cited unknown source: raw=%s allowed_source_ids=%s",
            raw_output,
            allowed_source_ids,
        )
        raise ValueError("MediPhi returned a source reference outside the supplied snapshot")
    return {"review_output": review_output}


def _normalize_output(output: dict) -> dict:
    """Normalize bounded local-model JSON variations before strict contract validation."""
    source_refs = output.get("source_refs")
    if isinstance(source_refs, list):
        output["source_refs"] = [
            {"source_id": source_ref} if isinstance(source_ref, str) else source_ref
            for source_ref in source_refs
        ]

    confidence = output.get("confidence")
    if isinstance(confidence, str):
        confidence_scores = {"low": 0.3, "medium": 0.6, "high": 0.8}
        confidence_level, separator, confidence_explanation = confidence.partition("-")
        normalized_confidence = confidence_scores.get(confidence_level.strip().lower())
        if normalized_confidence is not None:
            output["confidence"] = normalized_confidence
            if separator and confidence_explanation.strip() and not output.get("reasoning"):
                output["reasoning"] = confidence_explanation.strip()

    return output


def build_chartreview_graph() -> StateGraph:
    graph = StateGraph(ChartReviewGraphState)
    graph.add_node(
        "generate_review",
        generate_review,
        metadata={
            "execute_in": "activity",
            "start_to_close_timeout": timedelta(
                seconds=settings.activity_start_to_close_timeout_seconds
            ),
            "retry_policy": RetryPolicy(maximum_attempts=settings.activity_max_attempts),
        },
    )
    graph.add_edge(START, "generate_review")
    graph.add_edge("generate_review", END)
    return graph
