"""Internal models for chartreview LangGraph orchestration."""

from folium.core.chart_review import ChartReviewInput, ChartReviewOutput, ChartReviewSourceChunk
from typing_extensions import TypedDict


class ChartReviewGraphState(TypedDict):
    """State carried between chartreview graph nodes."""

    review_input: ChartReviewInput
    historical_source_chunks: list[ChartReviewSourceChunk]
    history_search_terms: list[str]
    review_output: ChartReviewOutput
