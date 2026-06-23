from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select

from app.dependencies.db_helpers import get_or_404, validate_mileage, apply_updates
from app.database.session import get_db
from app.dependencies.pagination import PaginationParams, paginate
from app.models.enums import MaintenanceType
from app.models.maintainence import MaintenanceRecord
from app.models.service_provider import ServiceProvider
from app.models.vehicle import Vehicle
from app.schemas.maintainence import (
    MaintenanceRecordCreate,
    MaintenanceRecordResponse,
    MaintenanceRecordUpdate,
)
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/maintenance-records", tags=["Maintenance Records"])


@router.post("/", response_model=MaintenanceRecordResponse)
def create_maintenance_record(
    record: MaintenanceRecordCreate, db: Session = Depends(get_db)
):
    vehicle = get_or_404(db, Vehicle, record.vehicle_id)

    validate_mileage(record.mileage_at_service, vehicle)

    if record.service_provider_id is not None:
        get_or_404(db, ServiceProvider, record.service_provider_id)

    new_record = MaintenanceRecord(**record.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.get("/", response_model=PaginatedResponse[MaintenanceRecordResponse])
def get_maintenance_records(
    vehicle_id: Optional[int] = Query(default=None, description="Filter by vehicle"),
    maintenance_type: Optional[MaintenanceType] = Query(
        default=None, description="Filter by type"
    ),
    from_date: Optional[date] = Query(
        default=None, description="Service date on or after (YYYY-MM-DD)"
    ),
    to_date: Optional[date] = Query(
        default=None, description="Service date on or before (YYYY-MM-DD)"
    ),
    pagination: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db),
):
    data_query = select(MaintenanceRecord)
    count_query = select(func.count()).select_from(MaintenanceRecord)

    if vehicle_id is not None:
        data_query = data_query.where(MaintenanceRecord.vehicle_id == vehicle_id)
        count_query = count_query.where(MaintenanceRecord.vehicle_id == vehicle_id)
    if maintenance_type:
        data_query = data_query.where(
            MaintenanceRecord.maintenance_type == maintenance_type
        )
        count_query = count_query.where(
            MaintenanceRecord.maintenance_type == maintenance_type
        )
    if from_date:
        data_query = data_query.where(MaintenanceRecord.service_date >= from_date)
        count_query = count_query.where(MaintenanceRecord.service_date >= from_date)
    if to_date:
        data_query = data_query.where(MaintenanceRecord.service_date <= to_date)
        count_query = count_query.where(MaintenanceRecord.service_date <= to_date)

    return paginate(db, data_query, count_query, pagination)


@router.get("/{record_id}", response_model=MaintenanceRecordResponse)
def get_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, MaintenanceRecord, record_id)


@router.patch("/{record_id}", response_model=MaintenanceRecordResponse)
def patch_maintenance_record(
    record_id: int, record_data: MaintenanceRecordUpdate, db: Session = Depends(get_db)
):
    """Partially update a maintenance record — only the fields you send will change."""
    record = get_or_404(db, MaintenanceRecord, record_id)

    updates = record_data.model_dump(exclude_unset=True, exclude_none=True)

    if "mileage_at_service" in updates:
        target_vehicle_id = updates.get("vehicle_id", record.vehicle_id)
        vehicle = get_or_404(db, Vehicle, target_vehicle_id)
        validate_mileage(updates["mileage_at_service"], vehicle)

    if "service_provider_id" in updates:
        get_or_404(db, ServiceProvider, updates["service_provider_id"])

    return apply_updates(db, record, record_data, exclude_none=True)


@router.delete("/{record_id}")
def delete_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    record = get_or_404(db, MaintenanceRecord, record_id)
    db.delete(record)
    db.commit()
    return {"message": "Maintenance record deleted successfully"}
