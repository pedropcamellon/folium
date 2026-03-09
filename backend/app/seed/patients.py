"""Seed patient data with Miami context."""

from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Patient


async def seed_patients(session: AsyncSession) -> List[Patient]:
    """Seed initial patient data with realistic Miami names (bilingual context)."""
    # Check if patients already exist
    result = await session.execute(select(Patient).limit(1))
    if result.scalar_one_or_none():
        print("Patients already seeded")
        return []

    # Create patients with realistic Miami names
    patients = [
        Patient(
            medical_record_number="MRN-2026-001",
            first_name="María",
            last_name="García",
            date_of_birth=date(1978, 5, 15),
            gender="Female",
            contact_info="(305) 555-0101",
            email="maria.garcia@email.com",
            phone="(305) 555-0101",
            address="1234 Coral Way, Miami, FL 33145",
            emergency_contact="Carlos García (esposo) - (305) 555-0102",
        ),
        Patient(
            medical_record_number="MRN-2026-002",
            first_name="James",
            last_name="Thompson",
            date_of_birth=date(1995, 9, 22),
            gender="Male",
            contact_info="(786) 555-0203",
            email="j.thompson@email.com",
            phone="(786) 555-0203",
            address="567 Brickell Ave, Miami, FL 33131",
            emergency_contact="Sarah Thompson (Mother) - (786) 555-0204",
        ),
        Patient(
            medical_record_number="MRN-2026-003",
            first_name="Luis",
            last_name="Fernández",
            date_of_birth=date(1963, 11, 8),
            gender="Male",
            contact_info="(305) 555-0305",
            email="luis.fernandez@email.com",
            phone="(305) 555-0305",
            address="890 SW 8th St, Miami, FL 33135",
            emergency_contact="Ana Fernández (hija) - (305) 555-0306",
        ),
    ]

    session.add_all(patients)
    await session.commit()

    # Refresh to get IDs
    for patient in patients:
        await session.refresh(patient)

    print(f"Seeded {len(patients)} patients")
    return patients
