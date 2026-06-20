from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


class MaintenanceRecordBase(SQLModel):
    """Fields shared by the DB table and the request/response schemas."""

    maintenance_type: str
    service_date: date
    cost: float


class MaintenanceRecord(MaintenanceRecordBase, table=True):
    # __tablename__ = "maintenance_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: int = Field(foreign_key="vehicle.id")

    vehicle: Optional["Vehicle"] = Relationship(back_populates="maintenance_records")
