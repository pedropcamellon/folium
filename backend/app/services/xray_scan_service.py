"""Orchestration for provider-requested scans in the separate X-ray app."""

import logging
from uuid import UUID

import httpx

from app.config import settings
from app.core.database import async_session_maker
from app.models.db import XrayScan
from app.models.xray_scan import (
    XrayAnalysisResult,
    XrayScanCreate,
    XrayScanResponse,
    XrayScanStatus,
)
from app.repositories.xray_scan_repository import XrayScanRepository
from app.services.storage.factory import get_storage

logger = logging.getLogger(__name__)


class XrayScanService:
    def __init__(self, repository: XrayScanRepository):
        self._repository = repository

    async def create(self, scan_input: XrayScanCreate, requested_by: str) -> XrayScanResponse:
        scan = await self._repository.create(scan_input, requested_by)
        await self._repository.session.commit()
        return self._to_response(scan)

    async def get(self, scan_id: UUID, patient_id: UUID) -> XrayScanResponse | None:
        scan = await self._repository.get(scan_id)
        if scan is None or scan.patient_id != patient_id:
            return None
        return self._to_response(scan)

    async def list_for_patient(self, patient_id: UUID) -> list[XrayScanResponse]:
        scans = await self._repository.list_for_patient(patient_id)
        return [self._to_response(scan) for scan in scans]

    @staticmethod
    def _to_response(scan: XrayScan) -> XrayScanResponse:
        return XrayScanResponse(
            id=scan.id,
            patientId=scan.patient_id,
            clinicalDocumentId=scan.clinical_document_id,
            status=XrayScanStatus(scan.status),
            result=scan.result_json,
            failureMessage=scan.failure_message,
            createdAt=scan.created_at,
            updatedAt=scan.updated_at,
        )


async def process_xray_scan(scan_id: UUID) -> None:
    """Run one persisted scan without logging patient data or image contents."""
    async with async_session_maker() as session:
        repository = XrayScanRepository(session)
        scan = await repository.get(scan_id)
        if scan is None or scan.status != XrayScanStatus.PENDING.value:
            return
        scan.status = XrayScanStatus.PROCESSING.value
        await session.commit()

        try:
            attachment = await repository.get_image_attachment(scan)
            if attachment is None:
                raise ValueError("The X-ray attachment is no longer available")
            storage = await get_storage()
            image_bytes = await storage.download(attachment.storage_key)
            if not settings.XRAY_REVIEW_SERVICE_TOKEN:
                raise RuntimeError("X-ray review service token is not configured")
            timeout = httpx.Timeout(120.0, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{settings.XRAY_REVIEW_SERVICE_URL.rstrip('/')}/v1/analyze",
                    headers={"X-Review-Service-Token": settings.XRAY_REVIEW_SERVICE_TOKEN},
                    files={
                        "file": (
                            "image.jpg" if attachment.mime_type == "image/jpeg" else "image.png",
                            image_bytes,
                            attachment.mime_type,
                        )
                    },
                )
                response.raise_for_status()
            result = XrayAnalysisResult.model_validate(response.json())
            scan.result_json = result.model_dump(mode="json", by_alias=True)
            scan.status = XrayScanStatus.COMPLETE.value
            scan.failure_message = None
        except Exception:
            logger.exception("X-ray review processing failed for scan %s", scan_id)
            scan.status = XrayScanStatus.FAILED.value
            scan.failure_message = "The X-ray review could not be completed. Retry the scan."
        await session.commit()
