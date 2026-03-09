"""Document database model (SQLAlchemy)."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base

if TYPE_CHECKING:
    from app.models.db.patient import Patient
    from app.models.db.interaction import Interaction


class Document(Base):
    """Document model for database persistence."""

    __tablename__ = "document"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient.id", ondelete="CASCADE"), nullable=False, index=True
    )
    interaction_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("interaction.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Required fields
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Optional fields
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # JSON fields
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

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
    patient: Mapped["Patient"] = relationship("Patient", back_populates="documents")
    interaction: Mapped[Optional["Interaction"]] = relationship(
        "Interaction", back_populates="documents"
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, type={self.type}, patient_id={self.patient_id})>"
