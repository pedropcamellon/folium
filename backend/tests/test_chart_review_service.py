"""Tests for the LangGraph chart-review draft-support service."""

import pytest

from app.models.chart_review import ChartReviewInput, ChartReviewSourceChunk, ChartReviewSourceType
from app.services.chart_review_service import (
    ChartReviewOutputValidationError,
    ChartReviewService,
    MockChartReviewProvider,
)


def build_review_input() -> ChartReviewInput:
    """Build a fully synthetic review context for deterministic tests."""
    return ChartReviewInput(
        patient_id="patient-001",
        interaction_id="interaction-001",
        timeline=[
            ChartReviewSourceChunk(
                source_id="timeline-001",
                source_type=ChartReviewSourceType.TIMELINE,
                content="Synthetic timeline event.",
            )
        ],
        transcript=ChartReviewSourceChunk(
            source_id="transcript-001",
            source_type=ChartReviewSourceType.TRANSCRIPT,
            content="Synthetic voice note transcript.",
        ),
    )


@pytest.mark.asyncio
async def test_mock_provider_generates_deterministic_traceable_output() -> None:
    service = ChartReviewService(MockChartReviewProvider())

    output = await service.generate(build_review_input())

    assert output.summary == (
        "Draft support generated from synthetic context. Primary source: Synthetic timeline event."
    )
    assert output.confidence == 0.8
    assert [source_ref.source_id for source_ref in output.source_refs] == [
        "timeline-001",
        "transcript-001",
    ]


@pytest.mark.asyncio
async def test_invalid_provider_output_is_explicit_error() -> None:
    class InvalidProvider:
        async def review(self, review_input: ChartReviewInput) -> dict[str, object]:
            return {"summary": "Incomplete output"}

    service = ChartReviewService(InvalidProvider())

    with pytest.raises(ChartReviewOutputValidationError, match="invalid chart-review output"):
        await service.generate(build_review_input())
