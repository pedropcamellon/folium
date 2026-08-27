"""Internal models for chartreview LangGraph orchestration."""

from folium.core.chart_review import ChartReviewInput, ChartReviewOutput
from typing_extensions import TypedDict


class ChartReviewGraphState(TypedDict):
    """State carried between chartreview graph nodes."""

    review_input: ChartReviewInput
    review_output: ChartReviewOutput
