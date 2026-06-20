from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import FuelType

if TYPE_CHECKING:
    from app.models.maintainence import MaintenanceRecord


class VehicleBase(SQLModel):
    """Fields shared by the DB table and the request/response schemas."""

    make: str = Field(index=True)
    model: str
    year: int
    license_plate: str = Field(index=True)
    current_mileage: int = Field(ge=0)
    fuel_type: FuelType


class Vehicle(VehicleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    maintenance_records: List["MaintenanceRecord"] = Relationship(
        back_populates="vehicle"
    )