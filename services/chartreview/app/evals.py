"""Typed loading and validation for committed anonymized chart-review cases."""

from datetime import date, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class Patient(BaseModel):
    """Non-identifying patient attributes needed to create an evaluation case."""

    key: str = Field(min_length=1)
    age_at_active_encounter: int = Field(ge=0, le=130)
    date_of_birth: date
    gender: str = Field(min_length=1, max_length=20)


class Encounter(BaseModel):
    """An encounter used to build chart-review context."""

    key: str = Field(min_length=1)
    occurred_at: datetime
    title: str = Field(min_length=1)
    summary: str | None = None
    description: str | None = None
    note: str | None = None


class CaseFixture(BaseModel):
    """Native records from which an evaluation adapter creates context."""

    patient: Patient
    encounters: list[Encounter] = Field(min_length=1)
    active_encounter_key: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_encounters(self) -> "CaseFixture":
        encounter_keys = [encounter.key for encounter in self.encounters]
        if len(encounter_keys) != len(set(encounter_keys)):
            raise ValueError("fixture encounter keys must be unique")
        if self.active_encounter_key not in encounter_keys:
            raise ValueError("active_encounter_key must reference a fixture encounter")

        active_index = encounter_keys.index(self.active_encounter_key)
        if active_index != len(self.encounters) - 1:
            raise ValueError("the active encounter must be last")

        occurred_at = [encounter.occurred_at for encounter in self.encounters]
        if occurred_at != sorted(occurred_at):
            raise ValueError("fixture encounters must be chronological")
        return self


class OutputExpectation(BaseModel):
    """Deterministic assertions for the final structured draft."""

    summary_facts: list[str] = Field(min_length=1)
    missing_information: list[str] = Field(min_length=1)
    follow_up_questions: list[str] = Field(min_length=1)
    required_source_roles: list[str] = Field(min_length=1)
    forbidden_source_roles: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] | None = None

    @model_validator(mode="after")
    def validate_source_roles(self) -> "OutputExpectation":
        overlap = set(self.required_source_roles) & set(self.forbidden_source_roles)
        if overlap:
            raise ValueError(f"source roles cannot be required and forbidden: {sorted(overlap)}")
        return self


class HistoryDecisionExpectation(BaseModel):
    """Deterministic assertions for bounded historical retrieval."""

    should_retrieve: bool
    forbidden_search_terms: list[str] = Field(default_factory=list)
    expected_returned_source_roles: list[str] = Field(default_factory=list)


class ValidationExpectation(BaseModel):
    """Expected structured-output validation terminal state."""

    expected_status: Literal["valid", "invalid"]


class CaseExpectations(BaseModel):
    output: OutputExpectation
    history_decision: HistoryDecisionExpectation
    validation: ValidationExpectation


class ChartReviewBenchmarkCase(BaseModel):
    """Validated, committed anonymized benchmark case."""

    id: str = Field(min_length=1)
    version: int = Field(ge=1)
    description: str = Field(min_length=1)
    fixture: CaseFixture
    expected: CaseExpectations

    @model_validator(mode="after")
    def validate_source_roles(self) -> "ChartReviewBenchmarkCase":
        available_roles: set[str] = set()
        for encounter in self.fixture.encounters:
            role_prefix = (
                "active" if encounter.key == self.fixture.active_encounter_key else encounter.key
            )
            if encounter.summary:
                available_roles.add(f"{role_prefix}.summary")
            if encounter.description:
                available_roles.add(f"{role_prefix}.description")
            if encounter.note:
                available_roles.add(f"{role_prefix}.note")

        asserted_roles = (
            self.expected.output.required_source_roles
            + self.expected.output.forbidden_source_roles
            + self.expected.history_decision.expected_returned_source_roles
        )
        unknown_roles = sorted(set(asserted_roles) - available_roles)
        if unknown_roles:
            raise ValueError(f"source roles are not supplied by the fixture: {unknown_roles}")
        return self


def load_benchmark_case(path: Path) -> ChartReviewBenchmarkCase:
    """Load one committed YAML benchmark case without touching persistence."""

    with path.open(encoding="utf-8") as fixture_file:
        raw_case = yaml.safe_load(fixture_file)
    if not isinstance(raw_case, dict):
        raise TypeError("benchmark fixture must contain a YAML object")
    return ChartReviewBenchmarkCase.model_validate(raw_case)
