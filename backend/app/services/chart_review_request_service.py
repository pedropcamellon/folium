"""On-demand chart-review request orchestration for the interaction API."""

import logging
from uuid import UUID

from folium.core.chart_review import (
    ChartReviewConfidence,
    ChartReviewHistoryRequest,
    ChartReviewHistoryResponse,
    ChartReviewInput,
    ChartReviewSourceChunk,
    ChartReviewSourceType,
    ChartReviewStatus,
    ChartReviewWorkflowInput,
)

from app.models.chart_review import ChartReviewCitationResponse, ChartReviewResponse
from app.models.db.chart_review import ChartReview
from app.repositories.chart_review_repository import ChartReviewRepository
from app.services.chart_review_workflow_service import ChartReviewWorkflowService
from app.services.interaction_service import InteractionService

logger = logging.getLogger(__name__)


class ChartReviewRequestService:
    """Builds active-interaction snapshots and starts durable chart-review workflows."""

    def __init__(
        self,
        repository: ChartReviewRepository,
        interaction_service: InteractionService,
        workflow_service: ChartReviewWorkflowService,
    ) -> None:
        self._repository = repository
        self._interaction_service = interaction_service
        self._workflow_service = workflow_service

    async def request_for_interaction(self, interaction_id: str) -> ChartReviewResponse:
        """Persist and generate a draft review for an explicitly selected interaction."""
        interaction = await self._interaction_service.get_by_id(interaction_id)
        review_input = await self._build_input(interaction_id)
        chart_review = await self._repository.create_queued(
            patient_id=UUID(str(interaction.patientId)),
            interaction_id=UUID(interaction_id),
            review_input=review_input,
        )
        await self._repository.session.commit()
        try:
            await self._workflow_service.start(
                ChartReviewWorkflowInput(review_id=str(chart_review.id), review_input=review_input)
            )
        except Exception:
            logger.exception("Chart review workflow dispatch failed for review %s", chart_review.id)
            await self._repository.fail(
                chart_review, "Chart review could not be started. Please try again."
            )
            return self._to_response(chart_review)

        await self._repository.session.commit()
        return self._to_response(chart_review)

    async def get_for_interaction(self, interaction_id: str) -> ChartReviewResponse | None:
        """Return the latest persisted review for the selected interaction."""
        interaction = await self._interaction_service.get_by_id(interaction_id)
        review = await self._repository.get_latest_for_interaction(UUID(interaction_id))
        if review is None:
            return None
        if review.patient_id != UUID(str(interaction.patientId)):
            return None
        await self._refresh_workflow_result(review)
        return self._to_response(review)

    async def retrieve_prior_interaction_blocks(
        self, request: ChartReviewHistoryRequest
    ) -> ChartReviewHistoryResponse:
        """Return a bounded set of patient-scoped prior interaction source blocks."""
        active_interaction = await self._interaction_service.get_by_id(request.interaction_id)
        if str(active_interaction.patientId) != request.patient_id:
            raise ValueError("Chart-review history request does not match the active interaction")

        prior_interactions = await self._interaction_service.get_by_patient_id(request.patient_id)
        source_chunks: list[ChartReviewSourceChunk] = []
        for interaction in prior_interactions:
            if str(interaction.id) == request.interaction_id:
                continue
            for chunk in self._history_chunks_matching_terms(interaction, request.search_terms):
                source_chunks.append(
                    ChartReviewSourceChunk(
                        source_id=f"history-{chunk.source_id}",
                        source_type=chunk.source_type,
                        content=chunk.content,
                        resource_id=chunk.resource_id,
                        display_label=chunk.display_label,
                        content_role=chunk.content_role,
                        occurred_at=chunk.occurred_at,
                    )
                )
                if len(source_chunks) == request.max_blocks:
                    return ChartReviewHistoryResponse(source_chunks=source_chunks)
        return ChartReviewHistoryResponse(source_chunks=source_chunks)

    @staticmethod
    def _history_chunks_matching_terms(
        interaction, search_terms: list[str]
    ) -> list[ChartReviewSourceChunk]:
        """Return curated interaction blocks matching the agent's bounded search terms."""
        note_chunk = ChartReviewRequestService._transcript_chunk(interaction)
        candidate_chunks = ChartReviewRequestService._selected_interaction_chunks(interaction)
        if note_chunk is not None:
            candidate_chunks.append(note_chunk)
        return [
            chunk
            for chunk in candidate_chunks
            if any(term.casefold() in chunk.content.casefold() for term in search_terms)
        ]

    async def _build_input(self, interaction_id: str) -> ChartReviewInput:
        interaction = await self._interaction_service.get_by_id(interaction_id)
        selected_chunks = self._selected_interaction_chunks(interaction)
        return ChartReviewInput(
            patient_id=str(interaction.patientId),
            interaction_id=interaction_id,
            interactions=selected_chunks,
            documents=[],
            transcript=self._transcript_chunk(interaction),
        )

    async def _refresh_workflow_result(self, chart_review: ChartReview) -> None:
        if chart_review.status in {
            ChartReviewStatus.COMPLETED.value,
            ChartReviewStatus.FAILED.value,
        }:
            return
        try:
            status, output, failure_message = await self._workflow_service.get_result(
                self._workflow_service.workflow_id(str(chart_review.id)), None
            )
        except Exception:
            logger.exception(
                "Chart review workflow status lookup failed for review %s", chart_review.id
            )
            await self._repository.fail(
                chart_review, "Chart review status could not be retrieved. Please try again."
            )
            return

        if status == "completed" and output is not None:
            await self._repository.complete(chart_review, output)
        elif status == "failed":
            await self._repository.fail(
                chart_review, failure_message or "Chart review workflow failed."
            )
        else:
            chart_review.status = ChartReviewStatus.RUNNING.value
            await self._repository.session.commit()

    @staticmethod
    def _selected_interaction_chunks(interaction) -> list[ChartReviewSourceChunk]:
        chunks: list[ChartReviewSourceChunk] = []
        if interaction.summary:
            chunks.append(
                ChartReviewSourceChunk(
                    source_id=f"interaction-summary:{interaction.id}",
                    source_type=ChartReviewSourceType.INTERACTION,
                    content=interaction.summary,
                    resource_id=str(interaction.id),
                    display_label=interaction.title,
                    content_role="summary",
                    occurred_at=interaction.interactionDate,
                )
            )
        if interaction.description:
            chunks.append(
                ChartReviewSourceChunk(
                    source_id=f"interaction-description:{interaction.id}",
                    source_type=ChartReviewSourceType.INTERACTION,
                    content=interaction.description,
                    resource_id=str(interaction.id),
                    display_label=interaction.title,
                    content_role="description",
                    occurred_at=interaction.interactionDate,
                )
            )
        if not chunks:
            chunks.append(
                ChartReviewSourceChunk(
                    source_id=f"interaction:{interaction.id}",
                    source_type=ChartReviewSourceType.INTERACTION,
                    content=interaction.title,
                    resource_id=str(interaction.id),
                    display_label=interaction.title,
                    content_role="title",
                    occurred_at=interaction.interactionDate,
                )
            )
        return chunks

    @staticmethod
    def _transcript_chunk(interaction) -> ChartReviewSourceChunk | None:
        if not interaction.note:
            return None
        return ChartReviewSourceChunk(
            source_id=f"interaction-note:{interaction.id}",
            source_type=ChartReviewSourceType.TRANSCRIPT,
            content=interaction.note,
            resource_id=str(interaction.id),
            display_label=interaction.title,
            content_role="voice-note transcript",
            occurred_at=interaction.interactionDate,
        )

    @staticmethod
    def _to_response(chart_review: ChartReview) -> ChartReviewResponse:
        output = chart_review.output_json or {}
        status = ChartReviewStatus(chart_review.status)
        source_refs = ChartReviewRequestService._public_source_refs(chart_review)
        return ChartReviewResponse(
            id=str(chart_review.id),
            interactionId=str(chart_review.interaction_id),
            status=status,
            summary=output.get("summary"),
            reasoning=output.get("reasoning"),
            missingInfo=output.get("missing_info", []),
            followUpQuestions=output.get("follow_up_questions", []),
            sourceRefs=source_refs,
            confidence=ChartReviewConfidence(chart_review.confidence)
            if chart_review.confidence
            else None,
            reviewFlags=chart_review.review_flags or [],
            failureMessage=chart_review.failure_message,
        )

    @staticmethod
    def _public_source_refs(chart_review: ChartReview) -> list[ChartReviewCitationResponse]:
        if ChartReviewStatus(chart_review.status) != ChartReviewStatus.COMPLETED:
            return []

        source_by_id = {
            source.source_id: source
            for source in ChartReviewInput.model_validate(chart_review.input_snapshot).source_chunks
        }
        return [
            ChartReviewCitationResponse(
                sourceType=source.source_type,
                resourceId=source.resource_id,
                displayLabel=source.display_label,
                contentRole=source.content_role,
                occurredAt=source.occurred_at,
            )
            for citation in chart_review.cited_source_refs
            if (source := source_by_id.get(citation.source_id)) is not None
        ]
