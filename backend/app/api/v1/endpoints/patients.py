"""Patient endpoints - API route handlers"""

from fastapi import APIRouter, Depends, status

from app.core.permissions import Permission
from app.core.rbac import require_permission
from app.models.patient import PatientCreate, PatientUpdate, PatientResponse
from app.services.patient_service import PatientService
from app.dependencies import get_patient_service

router = APIRouter(prefix="/patients")


@router.get("/", response_model=list[PatientResponse])
async def list_patients(
    _: object = Depends(require_permission(Permission.PATIENTS_READ)),
    service: PatientService = Depends(get_patient_service)
):
    """Get all patients"""
    return await service.get_all()


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    _: object = Depends(require_permission(Permission.PATIENTS_READ)),
    service: PatientService = Depends(get_patient_service)
):
    """Get patient by ID"""
    return await service.get_by_id(patient_id)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    _: object = Depends(require_permission(Permission.PATIENTS_CREATE)),
    service: PatientService = Depends(get_patient_service)
):
    """Create new patient"""
    return await service.create(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient: PatientUpdate,
    _: object = Depends(require_permission(Permission.PATIENTS_UPDATE)),
    service: PatientService = Depends(get_patient_service)
):
    """Update existing patient"""
    return await service.update(patient_id, patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    _: object = Depends(require_permission(Permission.PATIENTS_DELETE)),
    service: PatientService = Depends(get_patient_service)
):
    """Delete patient"""
    await service.delete(patient_id)
