"""Patient endpoints - API route handlers"""

from fastapi import APIRouter, Depends, status

from app.core.logging import setup_structured_logging
from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.dependencies import get_patient_service
from app.models.patient import PatientCreate, PatientResponse, PatientUpdate
from app.models.user import User
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients")
logger = setup_structured_logging("backend")


@router.get("/", response_model=list[PatientResponse])
async def list_patients(
    current_user: User = Depends(require_permission(Permission.PATIENTS_READ)),
    service: PatientService = Depends(get_patient_service),
):
    """Get all patients"""
    logger.audit(
        action="patients_list_accessed",
        user_id=str(current_user.id),
        method="GET",
        endpoint="/api/v1/patients",
    )
    return await service.get_all()


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: User = Depends(require_permission(Permission.PATIENTS_READ)),
    service: PatientService = Depends(get_patient_service),
):
    """Get patient by ID"""
    logger.audit(
        action="patient_record_accessed",
        user_id=str(current_user.id),
        patient_id=patient_id,
        method="GET",
        endpoint=f"/api/v1/patients/{patient_id}",
    )
    return await service.get_by_id(patient_id)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    current_user: User = Depends(require_permission(Permission.PATIENTS_CREATE)),
    service: PatientService = Depends(get_patient_service),
):
    """Create new patient"""
    result = await service.create(patient)
    logger.audit(
        action="patient_record_created",
        user_id=str(current_user.id),
        patient_id=str(result.id),
        method="POST",
        endpoint="/api/v1/patients",
    )
    return result


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient: PatientUpdate,
    current_user: User = Depends(require_permission(Permission.PATIENTS_UPDATE)),
    service: PatientService = Depends(get_patient_service),
):
    """Update existing patient"""
    logger.audit(
        action="patient_record_updated",
        user_id=str(current_user.id),
        patient_id=patient_id,
        method="PUT",
        endpoint=f"/api/v1/patients/{patient_id}",
    )
    return await service.update(patient_id, patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    current_user: User = Depends(require_permission(Permission.PATIENTS_DELETE)),
    service: PatientService = Depends(get_patient_service),
):
    """Delete patient"""
    logger.audit(
        action="patient_record_deleted",
        user_id=str(current_user.id),
        patient_id=patient_id,
        method="DELETE",
        endpoint=f"/api/v1/patients/{patient_id}",
    )
    await service.delete(patient_id)
