import pytest
from pydantic import ValidationError

from app.models.xray_scan import XrayAnalysisResult, XrayScanCreate, XrayScanStatus


def test_scan_request_uses_public_camel_case_fields() -> None:
    request = XrayScanCreate(
        patientId="4e99de40-d971-4d03-a84a-4dfb731dc7d6",
        clinicalDocumentId="2d4976bc-4555-450e-ad88-153d0473bb1d",
    )

    assert request.model_dump(by_alias=True) == {
        "patientId": request.patient_id,
        "clinicalDocumentId": request.clinical_document_id,
    }


def test_analysis_contract_requires_provider_review_and_valid_scores() -> None:
    result = XrayAnalysisResult.model_validate(
        {
            "findings": [{"label": "Lung Lesion", "score": 0.7}],
            "modelRepository": "reference/model",
            "modelRevision": "revision",
            "reviewRequired": True,
            "disclaimer": "Research only.",
        }
    )

    assert result.review_required is True
    assert result.findings[0].score == 0.7
    assert result.model_dump(by_alias=True)["modelRepository"] == "reference/model"

    with pytest.raises(ValidationError):
        XrayAnalysisResult.model_validate(
            {
                "findings": [{"label": "Lung Lesion", "score": 1.1}],
                "modelRepository": "reference/model",
                "modelRevision": "revision",
                "reviewRequired": False,
                "disclaimer": "Research only.",
            }
        )


def test_scan_statuses_use_the_public_workflow_values() -> None:
    assert [status.value for status in XrayScanStatus] == [
        "PENDING",
        "PROCESSING",
        "COMPLETE",
        "FAILED",
    ]
