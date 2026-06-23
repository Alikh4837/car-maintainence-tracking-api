from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, col, select
from pydantic import BaseModel

from collections.abc import Sequence
from app.database.session import get_db
from app.models.enums import MaintenanceType
from app.models.maintainence import MaintenanceRecord
from app.models.vehicle import Vehicle

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class UpcomingServiceAlert(BaseModel):
    record_id: int
    vehicle_id: int
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    license_plate: str
    maintenance_type: MaintenanceType
    next_service_due_date: date
    days_until_due: int


def _build_alert(
    record: MaintenanceRecord, vehicle: Vehicle, today: date
) -> UpcomingServiceAlert:
    """Build a single alert object from a record and its vehicle."""
    return UpcomingServiceAlert(
        record_id=record.id or 0,
        vehicle_id=vehicle.id or 0,
        vehicle_make=vehicle.make,
        vehicle_model=vehicle.model,
        vehicle_year=vehicle.year,
        license_plate=vehicle.license_plate,
        maintenance_type=record.maintenance_type,
        next_service_due_date=record.next_service_due_date,  # type: ignore[arg-type]
        days_until_due=(record.next_service_due_date - today).days,  # type: ignore[operator]
    )


def _build_alerts_from_records(
    records: Sequence[MaintenanceRecord], db: Session, today: date
) -> list[UpcomingServiceAlert]:
    """Convert a list of maintenance records into alert objects."""
    alerts = []
    for record in records:
        vehicle = db.get(Vehicle, record.vehicle_id)
        if not vehicle:
            continue
        alerts.append(_build_alert(record, vehicle, today))
    return alerts


@router.get("/upcoming", response_model=list[UpcomingServiceAlert])
def get_upcoming_services(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Return services due within this many days from today",
    ),
    db: Session = Depends(get_db),
):
    """Returns all maintenance records due within the specified number of days."""
    today = date.today()
    cutoff = today + timedelta(days=days)

    records = db.exec(
        select(MaintenanceRecord)
        .where(col(MaintenanceRecord.next_service_due_date).is_not(None))
        .where(col(MaintenanceRecord.next_service_due_date) >= today)
        .where(col(MaintenanceRecord.next_service_due_date) <= cutoff)
        .order_by(col(MaintenanceRecord.next_service_due_date))
    ).all()

    return _build_alerts_from_records(records, db, today)


@router.get("/overdue", response_model=list[UpcomingServiceAlert])
def get_overdue_services(db: Session = Depends(get_db)):
    """Returns all maintenance records whose next service date has already passed."""
    today = date.today()

    records = db.exec(
        select(MaintenanceRecord)
        .where(col(MaintenanceRecord.next_service_due_date).is_not(None))
        .where(col(MaintenanceRecord.next_service_due_date) < today)
        .order_by(col(MaintenanceRecord.next_service_due_date))
    ).all()

    return _build_alerts_from_records(records, db, today)
