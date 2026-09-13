"""Chart-review prompt registry coverage."""

import pytest

from app.prompts import chart_review_prompt_path


def test_chart_review_prompt_v1_resolves_to_the_frozen_baseline() -> None:
    prompt_path = chart_review_prompt_path("v1")

    assert prompt_path.name == "chart_review_v1.md"
    assert prompt_path.is_file()


def test_chart_review_prompt_registry_rejects_unknown_versions() -> None:
    with pytest.raises(ValueError, match="unsupported chart-review prompt version 'v2'"):
        chart_review_prompt_path("v2")