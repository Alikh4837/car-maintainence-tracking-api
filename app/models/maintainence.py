from datetime import date
from typing import Optional, TYPE_CHECKING

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import MaintenanceType

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


class MaintenanceRecordBase(SQLModel):
    """Fields shared by the DB table and the request/response schemas."""

    maintenance_type: MaintenanceType
    service_date: date
    cost: float = Field(gt=0)

    @field_validator("service_date")
    @classmethod
    def service_date_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("service_date cannot be in the future")
        return value


class MaintenanceRecord(MaintenanceRecordBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: int = Field(foreign_key="vehicle.id")

    vehicle: Optional["Vehicle"] = Relationship(back_populates="maintenance_records")