"""Database operations for X-ray review jobs."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import ClinicalDocument, XrayScan
from app.models.db.clinical import Attachment
from app.models.xray_scan import XrayScanCreate, XrayScanStatus


class XrayScanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, scan_input: XrayScanCreate, requested_by: str) -> XrayScan:
        document = await self.session.scalar(
            select(ClinicalDocument).where(
                ClinicalDocument.id == scan_input.clinical_document_id,
                ClinicalDocument.patient_id == scan_input.patient_id,
            )
        )
        if document is None:
            raise ValueError("The imaging document was not found for this patient")
        attachments = await self.session.scalars(
            select(Attachment).where(Attachment.clinical_document_id == document.id)
        )
        if not any(item.mime_type in {"image/jpeg", "image/png"} for item in attachments):
            raise ValueError("X-ray review requires a JPEG or PNG image attachment")
        scan = XrayScan(
            patient_id=scan_input.patient_id,
            clinical_document_id=scan_input.clinical_document_id,
            requested_by=requested_by,
            status=XrayScanStatus.PENDING.value,
        )
        self.session.add(scan)
        await self.session.flush()
        return scan

    async def get(self, scan_id: UUID) -> XrayScan | None:
        return await self.session.scalar(select(XrayScan).where(XrayScan.id == scan_id))

    async def list_for_patient(self, patient_id: UUID) -> list[XrayScan]:
        result = await self.session.scalars(
            select(XrayScan)
            .where(XrayScan.patient_id == patient_id)
            .order_by(XrayScan.created_at.desc())
        )
        return list(result)

    async def get_image_attachment(self, scan: XrayScan) -> Attachment | None:
        result = await self.session.execute(
            select(Attachment).where(
                Attachment.clinical_document_id == scan.clinical_document_id,
                Attachment.mime_type.in_(("image/jpeg", "image/png")),
            )
        )
        return result.scalars().first()
