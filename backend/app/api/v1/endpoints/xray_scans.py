"""Provider-facing routes for the separately deployed X-ray review app."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.logging import setup_structured_logging
from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.models.user import User
from app.models.xray_scan import XrayScanCreate, XrayScanResponse
from app.repositories.xray_scan_repository import XrayScanRepository
from app.services.xray_scan_service import XrayScanService, process_xray_scan

router = APIRouter(prefix="/xray-scans", tags=["xray-review"])
logger = setup_structured_logging("backend")


def get_xray_scan_service(
    session: AsyncSession = Depends(get_async_session),
) -> XrayScanService:
    return XrayScanService(XrayScanRepository(session))


@router.post("/", response_model=XrayScanResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_xray_scan(
    scan_input: XrayScanCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_permission(Permission.DOCUMENTS_CREATE)),
    service: XrayScanService = Depends(get_xray_scan_service),
) -> XrayScanResponse:
    try:
        scan = await service.create(scan_input, str(user.id))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    logger.audit(
        action="xray_review_requested",
        user_id=str(user.id),
        patient_id=str(scan.patient_id),
        scan_id=str(scan.id),
    )
    background_tasks.add_task(process_xray_scan, scan.id)
    return scan


@router.get("/", response_model=list[XrayScanResponse])
async def list_xray_scans(
    patient_id: UUID = Query(..., alias="patientId"),
    user: User = Depends(require_permission(Permission.DOCUMENTS_READ)),
    service: XrayScanService = Depends(get_xray_scan_service),
) -> list[XrayScanResponse]:
    scans = await service.list_for_patient(patient_id)
    for scan in scans:
        logger.audit(
            action="xray_review_status_read",
            user_id=str(user.id),
            patient_id=str(scan.patient_id),
            scan_id=str(scan.id),
        )
    return scans


@router.get("/{scan_id}", response_model=XrayScanResponse)
async def get_xray_scan(
    scan_id: UUID,
    patient_id: UUID = Query(..., alias="patientId"),
    user: User = Depends(require_permission(Permission.DOCUMENTS_READ)),
    service: XrayScanService = Depends(get_xray_scan_service),
) -> XrayScanResponse:
    scan = await service.get(scan_id, patient_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="X-ray review not found"
        )
    logger.audit(
        action="xray_review_status_read",
        user_id=str(user.id),
        patient_id=str(scan.patient_id),
        scan_id=str(scan.id),
    )
    return scan
