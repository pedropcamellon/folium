import asyncio

from temporalio.client import Client
from temporalio.contrib.langgraph import LangGraphPlugin
from temporalio.worker import Worker

from app.config import settings
from app.graph import build_chartreview_graph
from app.workflow import ChartReviewWorkflow


async def main() -> None:
    client = await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)
    plugin = LangGraphPlugin(graphs={"chartreview": build_chartreview_graph()})
    worker = Worker(
        client,
        task_queue=settings.chartreview_task_queue,
        workflows=[ChartReviewWorkflow],
        plugins=[plugin],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
