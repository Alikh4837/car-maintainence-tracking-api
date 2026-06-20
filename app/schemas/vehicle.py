from typing import List

from app.models.vehicle import VehicleBase
from app.schemas.maintainence import MaintenanceRecordResponse


class VehicleCreate(VehicleBase):
    """Payload for creating/updating a vehicle — same fields as the table, no id."""

    pass


class VehicleResponse(VehicleBase):
    """What we return to the client — adds the generated id and its service history."""

    id: int
    maintenance_records: List[MaintenanceRecordResponse] = []
