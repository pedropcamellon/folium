"""Internal models for chartreview LangGraph orchestration."""

from typing import Annotated, Literal

from folium.core.chart_review import (
    ChartReviewInput,
    ChartReviewOutput,
    ChartReviewSourceChunk,
)
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import TypedDict

PlanText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=240)
]


class SearchHistoryPlan(BaseModel):
    """Concise evidence plan for an approved prior-interaction lookup."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome: Literal["search_history"]
    factual_gap: PlanText
    evidence_objective: PlanText
    evidence_scope: Literal["approved_prior_interactions"]
    success_condition: Literal["approved_block_returned"]
    stop_policy: Literal["bounded_history"]


class NoSearchPlan(BaseModel):
    """Explicit decision to draft without requesting historical evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome: Literal["no_search"]
    reason: Literal["active_context_sufficient", "permitted_history_not_useful"]


ChartReviewHistoryPlan = SearchHistoryPlan | NoSearchPlan

class SearchHistoryAction(BaseModel):
    """Lexical search action that cannot change the accepted evidence plan."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    action: Literal["search_history"]
    search_terms: list[
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    ] = Field(min_length=1, max_length=3)


class StopHistoryAction(BaseModel):
    """Stop when no useful permitted search terms remain."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    action: Literal["stop"]
    reason: Literal["no_new_terms", "permitted_history_not_useful"]


ChartReviewHistoryAction = SearchHistoryAction | StopHistoryAction


class ChartReviewGraphInputState(TypedDict):
    """Required state passed to the workflow."""

    review_input: ChartReviewInput


class ChartReviewGraphState(ChartReviewGraphInputState, total=False):
    """State carried between chartreview graph nodes."""

    history_plan: ChartReviewHistoryPlan
    history_action: ChartReviewHistoryAction
    historical_source_chunks: list[ChartReviewSourceChunk]
    history_search_terms: list[str]
    history_retrieval_attempts: int
    failed_history_search_terms: list[str]
    review_output: ChartReviewOutput
