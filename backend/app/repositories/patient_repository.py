"""Patient repository - Data access layer"""

from typing import List, Optional
from datetime import datetime, timedelta
from app.repositories.base import BaseRepository


class PatientRepository(BaseRepository):
    """In-memory patient repository (MVP implementation)"""

    def __init__(self):
        self._patients = {}
        self._seed_data()

    async def get_all(self) -> List[dict]:
        """Get all patients"""
        return list(self._patients.values())

    async def get_by_id(self, patient_id: str) -> Optional[dict]:
        """Get patient by ID"""
        return self._patients.get(patient_id)

    async def create(self, patient_data: dict) -> dict:
        """Create new patient"""
        patient_id = self._generate_id()
        patient = {"id": patient_id, **patient_data, "createdAt": self._now(), "updatedAt": None}
        self._patients[patient_id] = patient
        return patient

    async def update(self, patient_id: str, patient_data: dict) -> Optional[dict]:
        """Update existing patient"""
        if patient_id not in self._patients:
            return None

        # Update only provided fields
        for key, value in patient_data.items():
            if value is not None:
                self._patients[patient_id][key] = value

        self._patients[patient_id]["updatedAt"] = self._now()
        return self._patients[patient_id]

    async def delete(self, patient_id: str) -> bool:
        """Delete patient"""
        if patient_id in self._patients:
            del self._patients[patient_id]
            return True
        return False

    def _seed_data(self):
        """Seed initial patient data"""
        sample_patients = [
            {
                "id": "patient-001",
                "medicalRecordNumber": "MRN-2024-001",
                "firstName": "John",
                "lastName": "Doe",
                "dateOfBirth": (datetime.now() - timedelta(days=365 * 45)).isoformat(),
                "gender": "Male",
                "contactInfo": "(555) 123-4567",
                "email": "john.doe@email.com",
                "phone": "(555) 123-4567",
                "address": "123 Main St, Anytown, USA",
                "emergencyContact": "Jane Doe - (555) 987-6543",
                "createdAt": self._now().isoformat(),
                "updatedAt": None,
            },
            {
                "id": "patient-002",
                "medicalRecordNumber": "MRN-2024-002",
                "firstName": "Sarah",
                "lastName": "Johnson",
                "dateOfBirth": (datetime.now() - timedelta(days=365 * 32)).isoformat(),
                "gender": "Female",
                "contactInfo": "(555) 234-5678",
                "email": "sarah.j@email.com",
                "phone": "(555) 234-5678",
                "address": "456 Oak Ave, Springfield, USA",
                "emergencyContact": "Mike Johnson - (555) 876-5432",
                "createdAt": self._now().isoformat(),
                "updatedAt": None,
            },
            {
                "id": "patient-003",
                "medicalRecordNumber": "MRN-2024-003",
                "firstName": "Michael",
                "lastName": "Chen",
                "dateOfBirth": (datetime.now() - timedelta(days=365 * 28)).isoformat(),
                "gender": "Male",
                "contactInfo": "(555) 345-6789",
                "email": "m.chen@email.com",
                "phone": "(555) 345-6789",
                "address": "789 Pine Rd, Riverside, USA",
                "emergencyContact": "Lisa Chen - (555) 765-4321",
                "createdAt": self._now().isoformat(),
                "updatedAt": None,
            },
        ]

        for patient in sample_patients:
            self._patients[patient["id"]] = patient
