from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from app.services.chart_review_request_service import ChartReviewRequestService


def test_active_note_chunk_uses_the_latest_final_narrative() -> None:
    created_at = datetime(2026, 11, 12, tzinfo=UTC)
    encounter = SimpleNamespace(
        id=uuid4(),
        title="Synthetic cough and fever encounter",
        started_at=created_at,
        narratives=[
            SimpleNamespace(
                content="Preliminary content.",
                status="preliminary",
                created_at=created_at,
            ),
            SimpleNamespace(
                content="Final active encounter facts.",
                status="final",
                created_at=created_at + timedelta(minutes=1),
            ),
        ],
    )

    note_chunk = ChartReviewRequestService._transcript_chunk(encounter)

    assert note_chunk is not None
    assert note_chunk.content == "Final active encounter facts."
    assert note_chunk.content_role == "voice-note transcript"


def test_active_encounter_chunks_include_all_clinical_context() -> None:
    occurred_at = datetime(2026, 11, 12, tzinfo=UTC)
    encounter = SimpleNamespace(
        id=uuid4(),
        title="Current encounter",
        started_at=occurred_at,
        summary="Current summary.",
        description="Current description.",
        chief_complaint="Current complaint.",
        clinical_assessment="Current assessment.",
        treatment_plan="Current plan.",
        structured_summary={"finding": "Current structured finding."},
    )

    chunks = ChartReviewRequestService._selected_encounter_chunks(encounter)

    assert {chunk.content_role for chunk in chunks} == {
        "title",
        "summary",
        "description",
        "chief complaint",
        "clinical assessment",
        "treatment plan",
        "structured summary",
    }
    assert next(
        chunk for chunk in chunks if chunk.content_role == "structured summary"
    ).content == ('{"finding": "Current structured finding."}')
