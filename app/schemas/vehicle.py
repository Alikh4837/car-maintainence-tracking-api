from typing import List, Optional

from app.models.enums import FuelType
from app.models.vehicle import VehicleBase
from app.schemas.maintainence import MaintenanceRecordResponse


class VehicleCreate(VehicleBase):
    """Payload for creating/updating a vehicle — same fields as the table, no id."""

    pass


class VehicleUpdate(VehicleBase):
    """Payload for partial updates — every field is optional so callers
    only send what they want to change."""

    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None
    current_mileage: Optional[int] = None
    fuel_type: Optional[FuelType] = None


class VehicleResponse(VehicleBase):
    """What we return to the client — adds the generated id and its service history."""

    id: int
    maintenance_records: List[MaintenanceRecordResponse] = []