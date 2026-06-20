from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_db
from app.models.maintainence import MaintenanceRecord
from app.models.vehicle import Vehicle
from app.schemas.maintainence import MaintenanceRecordCreate, MaintenanceRecordResponse

router = APIRouter(prefix="/maintenance-records", tags=["Maintenance Records"])


@router.post("/", response_model=MaintenanceRecordResponse)
def create_maintenance_record(
    record: MaintenanceRecordCreate, db: Session = Depends(get_db)
):
    vehicle = db.get(Vehicle, record.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    new_record = MaintenanceRecord(**record.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.get("/", response_model=list[MaintenanceRecordResponse])
def get_maintenance_records(db: Session = Depends(get_db)):
    return db.exec(select(MaintenanceRecord)).all()


@router.get("/{record_id}", response_model=MaintenanceRecordResponse)
def get_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(MaintenanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return record


@router.put("/{record_id}", response_model=MaintenanceRecordResponse)
def update_maintenance_record(
    record_id: int, record_data: MaintenanceRecordCreate, db: Session = Depends(get_db)
):
    record = db.get(MaintenanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    record.vehicle_id = record_data.vehicle_id
    record.maintenance_type = record_data.maintenance_type
    record.service_date = record_data.service_date
    record.cost = record_data.cost

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
