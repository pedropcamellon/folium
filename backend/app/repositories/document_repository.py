"""Clinical document repository - Data access layer"""

from typing import Optional
from datetime import datetime, timedelta
from app.repositories.base import BaseRepository
from app.models.document import ClinicalDocumentType, get_type_label


class DocumentRepository(BaseRepository):
    """In-memory document repository (MVP implementation)"""

    def __init__(self):
        self._documents = {}
        self._seed_data()

    async def get_all(self) -> list[dict]:
        """Get all documents"""
        return list(self._documents.values())

    async def get_by_id(self, document_id: str) -> Optional[dict]:
        """Get document by ID"""
        return self._documents.get(document_id)

    async def get_by_patient_id(
        self, patient_id: str, types: Optional[list[str]] = None
    ) -> list[dict]:
        """Get all documents for a specific patient, optionally filtered by type"""
        documents = [doc for doc in self._documents.values() if doc.get("patientId") == patient_id]

        if types:
            documents = [doc for doc in documents if doc.get("type") in types]

        return documents

    async def get_by_interaction_id(self, interaction_id: str) -> list[dict]:
        """Get all documents linked to a specific interaction"""
        return [
            doc for doc in self._documents.values() if doc.get("interactionId") == interaction_id
        ]

    async def create(self, document_data: dict) -> dict:
        """Create new document"""
        document_id = self._generate_id()

        # Generate type label
        doc_type = document_data.get("type")
        type_label = get_type_label(ClinicalDocumentType(doc_type)) if doc_type else "Document"

        document = {
            "id": document_id,
            **document_data,
            "typeLabel": type_label,
            "createdAt": self._now().isoformat(),
            "updatedAt": None,
            "createdBy": "system",  # TODO: Get from auth context
            "updatedBy": None,
        }
        self._documents[document_id] = document
        return document

    async def update(self, document_id: str, document_data: dict) -> Optional[dict]:
        """Update existing document"""
        if document_id not in self._documents:
            return None

        # Update only provided fields
        for key, value in document_data.items():
            if value is not None:
                self._documents[document_id][key] = value

        # Update type label if type changed
        if "type" in document_data:
            doc_type = document_data["type"]
            self._documents[document_id]["typeLabel"] = get_type_label(
                ClinicalDocumentType(doc_type)
            )

        self._documents[document_id]["updatedAt"] = self._now().isoformat()
        self._documents[document_id]["updatedBy"] = "system"  # TODO: Get from auth context
        return self._documents[document_id]

    async def delete(self, document_id: str) -> bool:
        """Delete document"""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False

    def _seed_data(self):
        """Seed initial document data"""
        base_time = datetime.now()

        sample_documents = [
            {
                "id": "doc-001",
                "patientId": "patient-001",
                "type": "ClinicalNote",
                "typeLabel": "Note",
                "title": "Annual Physical Exam Notes",
                "summary": "Patient in good health. Vital signs normal.",
                "interactionId": "interaction-001",
                "metadata": {"format": "SOAP", "signed": True},
                "createdAt": (base_time - timedelta(days=30)).isoformat(),
                "updatedAt": None,
                "createdBy": "provider-001",
                "updatedBy": None,
            },
            {
                "id": "doc-002",
                "patientId": "patient-001",
                "type": "LabResult",
                "typeLabel": "Labs",
                "title": "Lipid Panel Results",
                "summary": "Cholesterol levels slightly elevated. Recommend dietary changes.",
                "interactionId": "interaction-002",
                "metadata": {
                    "results": {
                        "totalCholesterol": 215,
                        "HDL": 45,
                        "LDL": 145,
                        "triglycerides": 125,
                    },
                    "status": "Final",
                },
                "createdAt": (base_time - timedelta(days=23)).isoformat(),
                "updatedAt": None,
                "createdBy": "lab-system",
                "updatedBy": None,
            },
            {
                "id": "doc-003",
                "patientId": "patient-002",
                "type": "Prescription",
                "typeLabel": "Prescription",
                "title": "Lisinopril 10mg Prescription",
                "summary": "Blood pressure medication. Take once daily.",
                "interactionId": None,
                "metadata": {
                    "medication": "Lisinopril",
                    "dosage": "10mg",
                    "frequency": "Once daily",
                    "refills": 3,
                    "expires": (base_time + timedelta(days=365)).isoformat(),
                },
                "createdAt": (base_time - timedelta(days=60)).isoformat(),
                "updatedAt": None,
                "createdBy": "provider-001",
                "updatedBy": None,
            },
            {
                "id": "doc-004",
                "patientId": "patient-003",
                "type": "AdministrativeForm",
                "typeLabel": "Form",
                "title": "HIPAA Privacy Notice - Signed",
                "summary": "Patient acknowledged HIPAA privacy practices.",
                "interactionId": None,
                "metadata": {
                    "formType": "HIPAA",
                    "signedDate": (base_time - timedelta(days=90)).isoformat(),
                },
                "createdAt": (base_time - timedelta(days=90)).isoformat(),
                "updatedAt": None,
                "createdBy": "front-desk",
                "updatedBy": None,
            },
            {
                "id": "doc-005",
                "patientId": "patient-001",
                "type": "PatientUpload",
                "typeLabel": "Upload",
                "title": "Insurance Card - Front",
                "summary": "Patient uploaded insurance card image.",
                "interactionId": None,
                "metadata": {"fileType": "image/jpeg", "uploadedBy": "patient"},
                "createdAt": (base_time - timedelta(days=45)).isoformat(),
                "updatedAt": None,
                "createdBy": "patient-001",
                "updatedBy": None,
            },
        ]

        for document in sample_documents:
            self._documents[document["id"]] = document
