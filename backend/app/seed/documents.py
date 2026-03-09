"""Seed document data for patients."""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Patient, Interaction, Document


async def seed_documents(
    session: AsyncSession, patients: List[Patient], interactions: List[Interaction]
) -> None:
    """Seed documents including one attached to María's encounter."""
    if not patients:
        return

    # Check if documents already exist
    result = await session.execute(select(Document).limit(1))
    if result.scalar_one_or_none():
        print("Documents already seeded")
        return

    # Create documents including one attached to María's encounter
    documents = [
        Document(
            patient_id=patients[0].id,
            interaction_id=interactions[0].id if interactions else None,
            title="Chest X-Ray Results",
            file_name="chest-xray-2026-03-01.pdf",
            file_type="application/pdf",
            file_size=245678,
            storage_url="https://storage.example.com/docs/chest-xray-maria.pdf",
            category="imaging",
            uploaded_by="provider@southdrift.com",
        ),
        Document(
            patient_id=patients[0].id,
            title="Patient Intake Form",
            file_name="intake-form-maria-garcia.pdf",
            file_type="application/pdf",
            file_size=89234,
            storage_url="https://storage.example.com/docs/intake-maria.pdf",
            category="administrative",
            uploaded_by="staff@southdrift.com",
        ),
        Document(
            patient_id=patients[1].id,
            title="Lab Results - Blood Panel",
            file_name="lab-results-2026-02-28.pdf",
            file_type="application/pdf",
            file_size=156432,
            storage_url="https://storage.example.com/docs/lab-results-james.pdf",
            category="lab_results",
            uploaded_by="provider@southdrift.com",
        ),
    ]

    session.add_all(documents)
    await session.commit()

    print(f"Seeded {len(documents)} documents")
