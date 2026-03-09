"""Interaction database model (SQLAlchemy)."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base

if TYPE_CHECKING:
    from app.models.db.patient import Patient
    from app.models.db.document import Document


class Interaction(Base):
    """Interaction model for database persistence."""

    __tablename__ = "interaction"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Required fields
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_compliant: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    provider_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    provider_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audio_document_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # JSON fields
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    structured_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Clinical summary fields
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_assessment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    treatment_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit fields
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    updated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="interactions")
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="interaction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, type={self.type}, patient_id={self.patient_id})>"
