from folium.core.chart_review import (
    CHARTREVIEW_WORKFLOW_NAME,
    ChartReviewOutput,
    ChartReviewWorkflowInput,
)
from temporalio import workflow
from temporalio.contrib.langgraph import graph


@workflow.defn(name=CHARTREVIEW_WORKFLOW_NAME)
class ChartReviewWorkflow:
    @workflow.run
    async def run(self, workflow_input: ChartReviewWorkflowInput) -> ChartReviewOutput:
        result = (
            await graph("chartreview")
            .compile()
            .ainvoke({"review_input": workflow_input.review_input})
        )
        return result["review_output"]
