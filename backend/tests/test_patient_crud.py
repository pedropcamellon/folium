from datetime import date, datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import PatientNotFoundError
from app.models.db.patient import Patient
from app.models.patient import PatientResponse
from app.core.auth import current_active_user
from app.dependencies import get_patient_service
from app.api.v1.endpoints.patients import router as patients_router
from app.repositories.patient_repository import PatientRepository, require_active_patient
from app.services.patient_service import PatientService


class ScalarResult:
    def __init__(self, value: Patient):
        self.value = value

    def scalar_one_or_none(self) -> Patient:
        return self.value


class SessionStub:
    def __init__(self, patient: Patient):
        self.patient = patient
        self.deleted = False

    async def execute(self, _statement: object) -> ScalarResult:
        return ScalarResult(self.patient)

    async def scalar(self, _statement: object):
        return self.patient.id if self.patient.is_active else None

    async def flush(self) -> None:
        pass

    async def refresh(self, _patient: Patient) -> None:
        pass

    async def delete(self, _patient: Patient) -> None:
        self.deleted = True


class PatientServiceStub:
    def __init__(self, response: PatientResponse):
        self.response = response
        self.calls: list[str] = []

    async def get_all(self) -> list[PatientResponse]:
        self.calls.append("list")
        return [self.response]

    async def get_by_id(self, _patient_id: str) -> PatientResponse:
        self.calls.append("read")
        return self.response

    async def create(self, _patient: object) -> PatientResponse:
        self.calls.append("create")
        return self.response

    async def update(self, _patient_id: str, _patient: object) -> PatientResponse:
        self.calls.append("update")
        return self.response

    async def deactivate(self, _patient_id: str) -> bool:
        self.calls.append("deactivate")
        return True


@pytest.mark.asyncio
async def test_update_persists_all_fields_exposed_by_patient_update() -> None:
    patient_id = uuid4()
    patient = Patient(
        id=patient_id,
        medical_record_number="MRN-OLD",
        first_name="Sample",
        last_name="Patient",
        date_of_birth=date(1980, 1, 1),
        gender="unknown",
        contact_info="sample@example.invalid",
    )
    repository = PatientRepository(SessionStub(patient))

    updated = await repository.update(
        str(patient.id),
        {
            "medical_record_number": "MRN-NEW",
            "date_of_birth": date(1981, 2, 3),
            "id": uuid4(),
        },
    )

    assert updated is patient
    assert patient.medical_record_number == "MRN-NEW"
    assert patient.date_of_birth == date(1981, 2, 3)
    assert patient.id == patient_id


@pytest.mark.asyncio
async def test_deactivate_retains_patient_instead_of_deleting_it() -> None:
    patient = Patient(
        id=uuid4(),
        medical_record_number="MRN-1",
        first_name="Sample",
        last_name="Patient",
        date_of_birth=date(1980, 1, 1),
        gender="unknown",
        contact_info="sample@example.invalid",
    )
    session = SessionStub(patient)
    repository = PatientRepository(session)

    assert await repository.deactivate(str(patient.id))

    assert patient.is_active is False
    assert not session.deleted


@pytest.mark.asyncio
async def test_inactive_patients_cannot_receive_new_clinical_records() -> None:
    patient = Patient(
        id=uuid4(),
        medical_record_number="MRN-1",
        first_name="Sample",
        last_name="Patient",
        date_of_birth=date(1980, 1, 1),
        gender="unknown",
        contact_info="sample@example.invalid",
        is_active=False,
    )
    repository = PatientRepository(SessionStub(patient))

    with pytest.raises(PatientNotFoundError):
        await require_active_patient(repository.session, patient.id)


@pytest.mark.asyncio
async def test_invalid_patient_identifier_returns_not_found() -> None:
    patient = Patient(
        id=uuid4(),
        medical_record_number="MRN-1",
        first_name="Sample",
        last_name="Patient",
        date_of_birth=date(1980, 1, 1),
        gender="unknown",
        contact_info="sample@example.invalid",
    )
    repository = PatientRepository(SessionStub(patient))
    service = PatientService(repository)

    with pytest.raises(PatientNotFoundError):
        await service.get_by_id("not-a-uuid")


def test_patient_crud_routes_use_role_permissions_and_camel_case_contract() -> None:
    patient_id = uuid4()
    patient_response = PatientResponse(
        id=patient_id,
        medical_record_number="MRN-1",
        first_name="Sample",
        last_name="Patient",
        date_of_birth=date(1980, 1, 1),
        gender="unknown",
        contact_info="sample@example.invalid",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=None,
    )
    service = PatientServiceStub(patient_response)
    app = FastAPI()
    app.include_router(patients_router)
    app.dependency_overrides[current_active_user] = lambda: SimpleNamespace(
        id=uuid4(), role="provider"
    )
    app.dependency_overrides[get_patient_service] = lambda: service
    client = TestClient(app)

    assert client.get("/patients/").status_code == 200
    assert client.get(f"/patients/{patient_id}").json()["medicalRecordNumber"] == "MRN-1"
    created = client.post(
        "/patients/",
        json={
            "medicalRecordNumber": "MRN-1",
            "firstName": "Sample",
            "lastName": "Patient",
            "dateOfBirth": "1980-01-01",
            "gender": "unknown",
            "contactInfo": "sample@example.invalid",
        },
    )
    assert created.status_code == 201
    assert created.json()["createdAt"] == "2026-01-01T00:00:00Z"
    assert client.put(f"/patients/{patient_id}", json={"firstName": "Updated"}).status_code == 200
    assert client.delete(f"/patients/{patient_id}").status_code == 204
    assert service.calls == ["list", "read", "create", "update", "deactivate"]

    app.dependency_overrides[current_active_user] = lambda: SimpleNamespace(
        id=uuid4(), role="patient"
    )
    denied = client.get("/patients/")
    assert denied.status_code == 403
