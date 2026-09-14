"""Prompt registry for chart-review draft support."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
CHART_REVIEW_PROMPT_PATHS = {
    "v1": PROMPTS_DIR / "chart_review_v1.md",
}
CHART_REVIEW_HISTORY_DECISION_PROMPT_PATH = PROMPTS_DIR / "chart_review_history_decision.md"


def chart_review_prompt_path(version: str) -> Path:
    """Resolve a committed chart-review prompt version."""
    try:
        return CHART_REVIEW_PROMPT_PATHS[version]
    except KeyError as error:
        supported_versions = ", ".join(sorted(CHART_REVIEW_PROMPT_PATHS))
        raise ValueError(
            f"unsupported chart-review prompt version {version!r}; "
            f"supported versions: {supported_versions}"
        ) from error
