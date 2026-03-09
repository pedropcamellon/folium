"""Seed interaction data for patients."""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Patient, Interaction


async def seed_interactions(session: AsyncSession, patients: List[Patient]) -> List[Interaction]:
    """Seed interactions with full encounter for María García."""
    if not patients:
        return []

    # Check if interactions already exist
    result = await session.execute(select(Interaction).limit(1))
    if result.scalar_one_or_none():
        print("Interactions already seeded")
        return []

    # Create a full encounter for María García
    interactions = [
        Interaction(
            patient_id=patients[0].id,
            type="voice_note",
            title="Initial Consultation - Persistent Cough",
            interaction_date=datetime(2026, 3, 1, 10, 30, tzinfo=timezone.utc),
            description="Patient reports persistent cough for the past two weeks. "
            "No fever. Cough is worse at night. Has been taking over-the-counter "
            "cough medicine with minimal relief. Non-smoker. No recent travel.",
            summary="2-week persistent cough, worse at night, OTC meds ineffective",
            chief_complaint="Persistent cough for 2 weeks",
            clinical_assessment="Likely upper respiratory irritation, rule out bronchitis",
            treatment_plan="Prescribe inhaler, follow-up in 2 weeks",
            is_compliant=True,
            provider_name="Dr. Sarah Martinez",
            created_by="provider@southdrift.com",
        ),
        Interaction(
            patient_id=patients[0].id,
            type="clinic_visit",
            title="Follow-up Visit - Cough Improvement",
            interaction_date=datetime(2026, 3, 8, 14, 15, tzinfo=timezone.utc),
            description="Follow-up visit. Patient reports cough has improved with prescribed "
            "inhaler. No shortness of breath. Lung sounds clear. Continue current "
            "treatment plan. Recheck in 2 weeks if symptoms persist.",
            summary="Follow-up: cough improved with inhaler, lungs clear",
            chief_complaint="Follow-up for persistent cough",
            clinical_assessment="Significant improvement, lungs clear on auscultation",
            treatment_plan="Continue inhaler as needed, return if symptoms worsen",
            is_compliant=True,
            provider_name="Dr. Sarah Martinez",
            created_by="provider@southdrift.com",
        ),
        Interaction(
            patient_id=patients[1].id,
            type="phone_call",
            title="Lab Results Discussion",
            interaction_date=datetime(2026, 3, 5, 11, 0, tzinfo=timezone.utc),
            description="Patient calling about lab results. All values within normal range. "
            "Discussed nutrition and exercise recommendations.",
            summary="Lab results normal, discussed lifestyle modifications",
            is_compliant=True,
            created_by="staff@southdrift.com",
        ),
    ]

    session.add_all(interactions)
    await session.commit()

    # Refresh to get IDs
    for interaction in interactions:
        await session.refresh(interaction)

    print(f"Seeded {len(interactions)} interactions")
    return interactions
