"""LangGraph-backed service for synthetic chart-review draft support."""

from __future__ import annotations

from datetime import timedelta
from typing import Protocol, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError
from temporalio.common import RetryPolicy

from app.models.chart_review import ChartReviewInput, ChartReviewOutput


class ChartReviewOutputValidationError(ValueError):
    """Raised when a provider returns an invalid or untraceable draft."""


class ChartReviewProvider(Protocol):
    """Provider boundary for generating a structured chart-review draft."""

    async def review(self, review_input: ChartReviewInput) -> dict[str, object]:
        """Return an unvalidated structured draft for the supplied context."""


class ChartReviewGraphState(TypedDict):
    """LangGraph state passed between the workflow and provider node."""

    review_input: ChartReviewInput
    review_output: ChartReviewOutput


class MockChartReviewProvider:
    """Deterministic provider for local development and CI."""

    async def review(self, review_input: ChartReviewInput) -> dict[str, object]:
        source_chunks = review_input.source_chunks
        source_refs = [{"source_id": source.source_id} for source in source_chunks]
        missing_info = [] if review_input.transcript else ["No transcript was provided."]
        summary = "Draft support generated from synthetic context."

        if source_chunks:
            summary = f"{summary} Primary source: {source_chunks[0].content}"

        return {
            "summary": summary,
            "missing_info": missing_info,
            "follow_up_questions": ["What additional synthetic context should be reviewed?"],
            "source_refs": source_refs,
            "confidence": 0.8,
            "review_flags": [],
        }


class ChartReviewService:
    """Runs a single-call LangGraph chart-review draft workflow."""

    def __init__(self, provider: ChartReviewProvider, confidence_threshold: float = 0.7) -> None:
        self._provider = provider
        self._confidence_threshold = confidence_threshold
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(ChartReviewGraphState)
        graph.add_node(
            "generate_review",
            self._generate_review,
            metadata={
                "execute_in": "activity",
                "start_to_close_timeout": timedelta(seconds=30),
                "retry_policy": RetryPolicy(maximum_attempts=3),
            },
        )
        graph.add_edge(START, "generate_review")
        graph.add_edge("generate_review", END)
        return graph

    async def generate(self, review_input: ChartReviewInput) -> ChartReviewOutput:
        """Generate a validated draft review through the LangGraph workflow."""
        result = await self._graph.compile().ainvoke({"review_input": review_input})
        return result["review_output"]

    async def _generate_review(self, state: ChartReviewGraphState) -> dict[str, ChartReviewOutput]:
        review_input = state["review_input"]
        try:
            review_output = ChartReviewOutput.model_validate(
                await self._provider.review(review_input)
            )
        except ValidationError as exc:
            raise ChartReviewOutputValidationError(
                "Provider returned invalid chart-review output"
            ) from exc

        self._validate_source_refs(review_input, review_output)
        self._apply_confidence_flag(review_output)
        return {"review_output": review_output}

    def _validate_source_refs(
        self, review_input: ChartReviewInput, review_output: ChartReviewOutput
    ) -> None:
        valid_source_ids = {source.source_id for source in review_input.source_chunks}
        unknown_source_ids = {
            source_ref.source_id
            for source_ref in review_output.source_refs
            if source_ref.source_id not in valid_source_ids
        }
        if unknown_source_ids:
            unknown_sources = ", ".join(sorted(unknown_source_ids))
            raise ChartReviewOutputValidationError(
                f"Provider returned unknown chart-review source references: {unknown_sources}"
            )

    def _apply_confidence_flag(self, review_output: ChartReviewOutput) -> None:
        if review_output.confidence < self._confidence_threshold:
            review_flag = "Low confidence: review draft support output."
            if review_flag not in review_output.review_flags:
                review_output.review_flags.append(review_flag)
