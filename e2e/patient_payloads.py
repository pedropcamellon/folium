from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class PatientPayload:
    medical_record_number: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    contact_info: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


def build_provider_test_patient() -> PatientPayload:
    suffix = datetime.now(timezone.utc).strftime("%m%d%H%M%S")
    return PatientPayload(
        medical_record_number=f"E2E-{suffix}",
        first_name="Taylor",
        last_name=f"Flow{suffix[-4:]}",
        date_of_birth="1992-04-15",
        gender="Female",
        contact_info=f"e2e+{suffix}@folium.test",
    )


def build_updated_patient(source: PatientPayload) -> PatientPayload:
    return PatientPayload(
        medical_record_number=source.medical_record_number,
        first_name=source.first_name,
        last_name=source.last_name,
        date_of_birth=source.date_of_birth,
        gender=source.gender,
        contact_info=f"updated-{source.contact_info}",
    )