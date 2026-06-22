from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database.session import get_db
from app.models.enums import MaintenanceType
from app.models.maintainence import MaintenanceRecord
from app.models.service_provider import ServiceProvider
from app.models.vehicle import Vehicle
from app.schemas.maintainence import (
    MaintenanceRecordCreate,
    MaintenanceRecordResponse,
    MaintenanceRecordUpdate,
)

router = APIRouter(prefix="/maintenance-records", tags=["Maintenance Records"])


@router.post("/", response_model=MaintenanceRecordResponse)
def create_maintenance_record(
    record: MaintenanceRecordCreate, db: Session = Depends(get_db)
):
    vehicle = db.get(Vehicle, record.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if record.mileage_at_service > vehicle.current_mileage:
        raise HTTPException(
            status_code=400,
            detail=(
                f"mileage_at_service ({record.mileage_at_service}) cannot exceed "
                f"the vehicle's current mileage ({vehicle.current_mileage}). "
                "Update the vehicle's mileage first if the odometer has advanced."
            ),
        )

    if record.service_provider_id is not None:
        provider = db.get(ServiceProvider, record.service_provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

    new_record = MaintenanceRecord(**record.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.get("/", response_model=list[MaintenanceRecordResponse])
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
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
):
    query = select(MaintenanceRecord)

    if vehicle_id is not None:
        query = query.where(MaintenanceRecord.vehicle_id == vehicle_id)
    if maintenance_type:
        query = query.where(MaintenanceRecord.maintenance_type == maintenance_type)
    if from_date:
        query = query.where(MaintenanceRecord.service_date >= from_date)
    if to_date:
        query = query.where(MaintenanceRecord.service_date <= to_date)

    query = query.offset(offset).limit(limit)
    return db.exec(query).all()


@router.get("/{record_id}", response_model=MaintenanceRecordResponse)
def get_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(MaintenanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return record


@router.patch("/{record_id}", response_model=MaintenanceRecordResponse)
def patch_maintenance_record(
    record_id: int, record_data: MaintenanceRecordUpdate, db: Session = Depends(get_db)
):
    """Partially update a maintenance record — only the fields you send will change."""
    record = db.get(MaintenanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    updates = record_data.model_dump(exclude_unset=True, exclude_none=True)

    if "mileage_at_service" in updates:
        target_vehicle_id = updates.get("vehicle_id", record.vehicle_id)
        vehicle = db.get(Vehicle, target_vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        if updates["mileage_at_service"] > vehicle.current_mileage:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"mileage_at_service ({updates['mileage_at_service']}) cannot exceed "
                    f"the vehicle's current mileage ({vehicle.current_mileage})."
                ),
            )

    if "service_provider_id" in updates:
        provider = db.get(ServiceProvider, updates["service_provider_id"])
        if not provider:
            raise HTTPException(status_code=404, detail="Service provider not found")

    for field, value in updates.items():
        setattr(record, field, value)

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(MaintenanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    db.delete(record)
    db.commit()
    return {"message": "Maintenance record deleted successfully"}
