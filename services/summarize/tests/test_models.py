"""Tests for summarization service models."""

from app.models import StructuredSummary


def test_structured_summary_normalizes_list_objective() -> None:
    summary = StructuredSummary(
        chief_complaint="Mild residual cough",
        subjective="Patient reports improved sleep with no fever for the last 48 hours.",
        objective=[],
        assessment="Improving upper respiratory symptoms",
        plan="Continue supportive care",
        clinical_tags=["cough"],
        icd_codes=[],
        action_items=[],
    )

    assert summary.objective == ""


def test_structured_summary_normalizes_mixed_field_shapes() -> None:
    summary = StructuredSummary(
        chief_complaint=["Residual cough", "Sleep improved"],
        subjective={"history": "No fever for 48 hours"},
        objective=["No acute distress", "Breathing comfortably"],
        assessment="Improving viral syndrome",
        plan=["Hydration", "Return if fever recurs"],
        clinical_tags="cough",
        icd_codes="J06.9",
        action_items=None,
    )

    assert summary.chief_complaint == "Residual cough\nSleep improved"
    assert summary.subjective == "history: No fever for 48 hours"
    assert summary.objective == "No acute distress\nBreathing comfortably"
    assert summary.plan == "Hydration\nReturn if fever recurs"
    assert summary.clinical_tags == ["cough"]
    assert summary.icd_codes == ["J06.9"]
    assert summary.action_items == []
