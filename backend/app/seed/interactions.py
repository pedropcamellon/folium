"""Seed interaction data for patients."""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Patient, Interaction


async def seed_interactions(session: AsyncSession, patients: List[Patient]) -> List[Interaction]:
    """Seed interactions for all patients with diverse encounter types."""
    print(f"[DEBUG] seed_interactions called with {len(patients) if patients else 0} patients")

    if not patients:
        print("[DEBUG] No patients provided, returning empty list")
        return []

    # Check if interactions already exist
    print("[DEBUG] Checking if interactions already exist...")
    result = await session.execute(select(Interaction).limit(1))
    existing = result.scalar_one_or_none()
    if existing:
        print(f"[DEBUG] Interactions already seeded (found interaction: {existing.id})")
        return []

    print("[DEBUG] No existing interactions found, proceeding with seeding...")
    print(f"[DEBUG] Patient 0: {patients[0].id} - {patients[0].first_name} {patients[0].last_name}")
    if len(patients) > 1:
        print(
            f"[DEBUG] Patient 1: {patients[1].id} - {patients[1].first_name} {patients[1].last_name}"
        )
    if len(patients) > 2:
        print(
            f"[DEBUG] Patient 2: {patients[2].id} - {patients[2].first_name} {patients[2].last_name}"
        )

    # María García (Patient 0) - Full encounter timeline
    print("[DEBUG] Creating María García interactions...")
    maria_interactions = [
        Interaction(
            patient_id=patients[0].id,
            type="VoiceNote",
            title="Initial Consultation - Persistent Cough",
            interaction_date=datetime(2026, 3, 1, 10, 30, tzinfo=timezone.utc),
            description="Patient reports persistent cough for the past two weeks. "
            "No fever. Cough is worse at night. Has been taking over-the-counter "
            "cough medicine with minimal relief. Non-smoker. No recent travel.",
            summary="2-week persistent cough, worse at night, OTC meds ineffective",
            chief_complaint="Persistent cough for 2 weeks",
            clinical_assessment="Likely upper respiratory irritation, rule out bronchitis",
            treatment_plan="Prescribe inhaler, follow-up in 2 weeks",
            location="Telehealth",
            is_compliant=True,
            provider_id="prov-001",
            provider_name="Dr. Sarah Martinez",
            created_by="provider@southdrift.com",
        ),
        Interaction(
            patient_id=patients[0].id,
            type="Appointment",
            title="Follow-up Visit - Cough Improvement",
            interaction_date=datetime(2026, 3, 8, 14, 15, tzinfo=timezone.utc),
            description="Follow-up visit. Patient reports cough has improved with prescribed "
            "inhaler. No shortness of breath. Lung sounds clear. Continue current "
            "treatment plan. Recheck in 2 weeks if symptoms persist.",
            summary="Follow-up: cough improved with inhaler, lungs clear",
            chief_complaint="Follow-up for persistent cough",
            clinical_assessment="Significant improvement, lungs clear on auscultation",
            treatment_plan="Continue inhaler as needed, return if symptoms worsen",
            location="Main Clinic - Room 203",
            is_compliant=True,
            provider_id="prov-001",
            provider_name="Dr. Sarah Martinez",
            created_by="provider@southdrift.com",
        ),
        Interaction(
            patient_id=patients[0].id,
            type="LabWork",
            title="Annual Wellness - Lab Work",
            interaction_date=datetime(2026, 2, 15, 9, 0, tzinfo=timezone.utc),
            description="Annual wellness exam lab work. Fasting blood glucose, lipid panel, "
            "CBC. Patient advised to fast 12 hours before appointment.",
            summary="Annual labs: glucose 95, cholesterol 185, all values normal",
            location="Lab Services - Building B",
            is_compliant=True,
            provider_id="lab-tech-01",
            provider_name="Lab Tech Rodriguez",
            metadata_json={"tests": ["glucose", "lipid_panel", "cbc"], "fasting": True},
            created_by="lab@southdrift.com",
        ),
    ]

    # James Thompson (Patient 1) - Young adult preventive care
    print("[DEBUG] Creating James Thompson interactions...")
    james_interactions = [
        Interaction(
            patient_id=patients[1].id,
            type="Consultation",
            title="Lab Results Discussion",
            interaction_date=datetime(2026, 3, 5, 11, 0, tzinfo=timezone.utc),
            description="Patient calling about recent lab results. All values within normal range. "
            "Discussed nutrition and exercise recommendations for maintaining healthy lifestyle.",
            summary="Lab results normal, discussed lifestyle modifications",
            location="Telehealth",
            is_compliant=True,
            provider_id="nurse-02",
            provider_name="Nurse Emily Roberts",
            created_by="staff@southdrift.com",
        ),
        Interaction(
            patient_id=patients[1].id,
            type="Vaccination",
            title="Flu Vaccine - 2026 Season",
            interaction_date=datetime(2026, 2, 20, 15, 30, tzinfo=timezone.utc),
            description="Annual influenza vaccination administered. Patient tolerated well, "
            "no adverse reactions. Advised to monitor injection site for soreness.",
            summary="Flu vaccine administered, no adverse reactions",
            location="Main Clinic - Vaccination Station",
            is_compliant=True,
            provider_id="nurse-01",
            provider_name="Nurse Patricia Williams",
            metadata_json={"vaccine_type": "Quadrivalent", "lot_number": "FL2026-123456"},
            created_by="nurse@southdrift.com",
        ),
        Interaction(
            patient_id=patients[1].id,
            type="Appointment",
            title="Sports Physical Exam",
            interaction_date=datetime(2026, 1, 10, 10, 0, tzinfo=timezone.utc),
            description="Pre-participation sports physical examination. All systems reviewed. "
            "Cardiovascular exam normal. Vision 20/20. Cleared for athletic participation.",
            summary="Sports physical: all systems normal, cleared for sports",
            chief_complaint="Sports physical examination",
            clinical_assessment="Healthy, no contraindications for athletic participation",
            treatment_plan="Cleared for sports, return for annual check-up",
            location="Main Clinic - Room 105",
            is_compliant=True,
            provider_id="prov-002",
            provider_name="Dr. Michael Chen",
            created_by="provider@southdrift.com",
        ),
    ]

    # Luis Fernández (Patient 2) - Chronic condition management
    print("[DEBUG] Creating Luis Fernández interactions...")
    luis_interactions = [
        Interaction(
            patient_id=patients[2].id,
            type="Appointment",
            title="Hypertension Follow-up",
            interaction_date=datetime(2026, 3, 7, 9, 30, tzinfo=timezone.utc),
            description="Follow-up visit for hypertension management. BP 138/85 (improved from last visit). "
            "Patient reports taking medications as prescribed. Discussed DASH diet and sodium reduction. "
            "Continue current medication regimen.",
            summary="HTN follow-up: BP improved, continue current meds",
            chief_complaint="Hypertension follow-up",
            clinical_assessment="Hypertension improving with medication compliance",
            treatment_plan="Continue Lisinopril 10mg daily, low-sodium diet, recheck in 3 months",
            location="Main Clinic - Room 108",
            is_compliant=True,
            provider_id="prov-003",
            provider_name="Dr. Jennifer Lee",
            metadata_json={"blood_pressure": "138/85", "heart_rate": 72},
            created_by="provider@southdrift.com",
        ),
        Interaction(
            patient_id=patients[2].id,
            type="LabWork",
            title="Comprehensive Metabolic Panel",
            interaction_date=datetime(2026, 3, 1, 8, 15, tzinfo=timezone.utc),
            description="Comprehensive metabolic panel to monitor kidney function and electrolytes "
            "while on hypertension medication. Fasting labs.",
            summary="CMP: kidney function normal, electrolytes balanced",
            location="Lab Services - Building B",
            is_compliant=True,
            provider_id="lab-tech-01",
            provider_name="Lab Tech Rodriguez",
            metadata_json={"tests": ["cmp", "kidney_function"], "fasting": True},
            created_by="lab@southdrift.com",
        ),
        Interaction(
            patient_id=patients[2].id,
            type="VoiceNote",
            title="Medication Refill Request",
            interaction_date=datetime(2026, 2, 25, 16, 45, tzinfo=timezone.utc),
            description="Patient called requesting refill of Lisinopril. Pharmacy contacted. "
            "Refill approved for 90-day supply. Reminded patient of upcoming follow-up appointment.",
            summary="Lisinopril refill approved, 90-day supply",
            location="Telehealth",
            is_compliant=True,
            provider_id="nurse-02",
            provider_name="Nurse Emily Roberts",
            note="Pharmacy: CVS on SW 8th Street",
            created_by="staff@southdrift.com",
        ),
        Interaction(
            patient_id=patients[2].id,
            type="Appointment",
            title="Annual Wellness Exam",
            interaction_date=datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc),
            description="Annual wellness examination. Patient reports managing hypertension well. "
            "No new complaints. Physical exam unremarkable except for controlled HTN. "
            "Updated medication list and advance directives discussed.",
            summary="Annual exam: HTN controlled, overall health good",
            chief_complaint="Annual wellness examination",
            clinical_assessment="Hypertension controlled on medication, otherwise healthy",
            treatment_plan="Continue current HTN management, return in 3 months for BP check",
            location="Main Clinic - Room 108",
            is_compliant=True,
            provider_id="prov-003",
            provider_name="Dr. Jennifer Lee",
            created_by="provider@southdrift.com",
        ),
    ]

    interactions = maria_interactions + james_interactions + luis_interactions
    print(f"[DEBUG] Created {len(interactions)} interaction objects")
    print(
        f"[DEBUG] María: {len(maria_interactions)}, James: {len(james_interactions)}, Luis: {len(luis_interactions)}"
    )

    print("[DEBUG] Adding interactions to session...")
    session.add_all(interactions)

    print("[DEBUG] Committing transaction...")
    await session.commit()
    print("[DEBUG] Commit successful!")

    # Refresh to get IDs
    print("[DEBUG] Refreshing interactions to get database IDs...")
    for i, interaction in enumerate(interactions):
        await session.refresh(interaction)
        if i == 0:
            print(f"[DEBUG] First interaction ID: {interaction.id}")

    print(f"Seeded {len(interactions)} interactions for {len(patients)} patients")
    return interactions
