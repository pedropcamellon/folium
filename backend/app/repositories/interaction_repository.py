"""Patient interaction repository - Data access layer"""

from datetime import datetime, timedelta
from typing import Optional

from app.repositories.base import BaseRepository


class InteractionRepository(BaseRepository):
    """In-memory interaction repository (MVP implementation)"""

    def __init__(self):
        self._interactions = {}
        self._seed_data()

    async def get_all(self) -> list[dict]:
        """Get all interactions"""
        return list(self._interactions.values())

    async def get_by_id(self, interaction_id: str) -> Optional[dict]:
        """Get interaction by ID"""
        return self._interactions.get(interaction_id)

    async def get_by_patient_id(self, patient_id: str) -> list[dict]:
        """Get all interactions for a specific patient"""
        return [
            interaction
            for interaction in self._interactions.values()
            if interaction.get("patientId") == patient_id
        ]

    async def create(self, interaction_data: dict) -> dict:
        """Create new interaction"""
        interaction_id = self._generate_id()
        interaction = {
            "id": interaction_id,
            **interaction_data,
            "createdAt": self._now().isoformat(),
            "updatedAt": None,
            "createdBy": "system",  # TODO: Get from auth context
            "updatedBy": None,
        }
        self._interactions[interaction_id] = interaction
        return interaction

    async def update(self, interaction_id: str, interaction_data: dict) -> Optional[dict]:
        """Update existing interaction"""
        if interaction_id not in self._interactions:
            return None

        # Update only provided fields
        for key, value in interaction_data.items():
            if value is not None:
                self._interactions[interaction_id][key] = value

        self._interactions[interaction_id]["updatedAt"] = self._now().isoformat()
        self._interactions[interaction_id]["updatedBy"] = "system"  # TODO: Get from auth context
        return self._interactions[interaction_id]

    async def delete(self, interaction_id: str) -> bool:
        """Delete interaction"""
        if interaction_id in self._interactions:
            del self._interactions[interaction_id]
            return True
        return False

    def _seed_data(self):
        """Seed initial interaction data"""
        base_time = datetime.now()

        sample_interactions = [
            {
                "id": "interaction-001",
                "patientId": "patient-001",
                "type": "Appointment",
                "title": "Annual Physical Exam",
                "description": "Routine annual checkup",
                "interactionDate": (base_time - timedelta(days=30)).isoformat(),
                "location": "Main Clinic - Room 101",
                "providerId": "provider-001",
                "providerName": "Dr. Sarah Smith",
                "summary": "Patient in good health. Blood pressure normal. Recommended diet improvements.",
                "note": "Patient reports feeling well. No complaints.",
                "audioDocumentId": None,
                "isCompliant": True,
                "metadata": {"duration": "30min", "copay": "$25"},
                "createdAt": (base_time - timedelta(days=30)).isoformat(),
                "updatedAt": None,
                "createdBy": "system",
                "updatedBy": None,
            },
            {
                "id": "interaction-002",
                "patientId": "patient-001",
                "type": "LabWork",
                "title": "Blood Test - Lipid Panel",
                "description": "Follow-up lab work from annual physical",
                "interactionDate": (base_time - timedelta(days=25)).isoformat(),
                "location": "Lab Services - Building B",
                "providerId": "provider-002",
                "providerName": "Lab Tech Johnson",
                "summary": "Blood draw completed successfully. Results pending.",
                "note": None,
                "audioDocumentId": None,
                "isCompliant": True,
                "metadata": {"tests": ["cholesterol", "triglycerides", "HDL", "LDL"]},
                "createdAt": (base_time - timedelta(days=25)).isoformat(),
                "updatedAt": None,
                "createdBy": "system",
                "updatedBy": None,
            },
            {
                "id": "interaction-003",
                "patientId": "patient-002",
                "type": "VoiceNote",
                "title": "Follow-up Call - Medication Check",
                "description": "Phone consultation regarding new medication",
                "interactionDate": (base_time - timedelta(days=5)).isoformat(),
                "location": "Telehealth",
                "providerId": "provider-001",
                "providerName": "Dr. Sarah Smith",
                "summary": "Patient tolerating new medication well. No side effects reported.",
                "note": "Continue current dosage. Schedule follow-up in 2 weeks.",
                "audioDocumentId": "audio-doc-001",
                "isCompliant": True,
                "metadata": {"callDuration": "10min"},
                "createdAt": (base_time - timedelta(days=5)).isoformat(),
                "updatedAt": None,
                "createdBy": "system",
                "updatedBy": None,
            },
            {
                "id": "interaction-004",
                "patientId": "patient-003",
                "type": "Vaccination",
                "title": "Flu Shot - 2025",
                "description": "Annual influenza vaccination",
                "interactionDate": (base_time - timedelta(days=15)).isoformat(),
                "location": "Main Clinic - Vaccination Station",
                "providerId": "nurse-001",
                "providerName": "Nurse Emily Roberts",
                "summary": "Flu vaccine administered. No adverse reactions.",
                "note": "Patient advised to monitor for soreness at injection site.",
                "audioDocumentId": None,
                "isCompliant": True,
                "metadata": {"vaccine": "Quadrivalent", "lot": "FL2025-ABC123"},
                "createdAt": (base_time - timedelta(days=15)).isoformat(),
                "updatedAt": None,
                "createdBy": "system",
                "updatedBy": None,
            },
        ]

        for interaction in sample_interactions:
            self._interactions[interaction["id"]] = interaction
