"""Focused chart-review graph formatting coverage."""

import os

os.environ.setdefault("AI_SERVICE_BASE_URL", "http://localhost:8002")
os.environ.setdefault("CHARTREVIEW_BACKEND_URL", "http://localhost:8000")
os.environ.setdefault("CHARTREVIEW_INTERNAL_TOKEN", "test-token")

from folium.core.chart_review import ChartReviewInput, ChartReviewSourceChunk, ChartReviewSourceType

from app.graph import _format_active_context


def test_active_context_prioritizes_final_narrative_without_omitting_fields() -> None:
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
