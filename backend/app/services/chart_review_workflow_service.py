"""Temporal client wrapper for chart-review workflows."""

import asyncio

from folium.core.chart_review import (
    CHARTREVIEW_TASK_QUEUE,
    CHARTREVIEW_WORKFLOW_NAME,
    ChartReviewOutput,
    ChartReviewWorkflowInput,
)
from temporalio.client import Client, WorkflowExecutionStatus

from app.config import settings


class ChartReviewWorkflowService:
    def __init__(self) -> None:
        self._client: Client | None = None
        self._client_lock = asyncio.Lock()

    async def _get_client(self) -> Client:
        if self._client is None:
            async with self._client_lock:
                if self._client is None:
                    self._client = await Client.connect(
                        settings.TEMPORAL_ADDRESS, namespace=settings.TEMPORAL_NAMESPACE
                    )
        return self._client

    async def start(self, workflow_input: ChartReviewWorkflowInput) -> dict[str, str]:
        client = await self._get_client()
        handle = await client.start_workflow(
            CHARTREVIEW_WORKFLOW_NAME,
            workflow_input,
            id=self.workflow_id(workflow_input.review_id),
            task_queue=CHARTREVIEW_TASK_QUEUE,
        )
        return {
            "workflow_id": handle.id,
            "run_id": handle.result_run_id or handle.first_execution_run_id or handle.run_id or "",
        }

    @staticmethod
    def workflow_id(review_id: str) -> str:
        return f"chartreview-{review_id}"

    async def get_result(
        self, workflow_id: str, run_id: str | None
    ) -> tuple[str, ChartReviewOutput | None, str | None]:
        client = await self._get_client()
        handle = client.get_workflow_handle(workflow_id, run_id=run_id or None)
        description = await handle.describe()
        if description.status == WorkflowExecutionStatus.COMPLETED:
            result = await handle.result()
            output = ChartReviewOutput.model_validate(result)
            return "completed", output, None
        if description.status in {
            WorkflowExecutionStatus.FAILED,
            WorkflowExecutionStatus.CANCELED,
            WorkflowExecutionStatus.TERMINATED,
            WorkflowExecutionStatus.TIMED_OUT,
        }:
            return "failed", None, "Chart review workflow did not complete."
        return "running", None, None
