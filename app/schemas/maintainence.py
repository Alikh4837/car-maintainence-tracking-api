from app.models.maintainence import MaintenanceRecordBase


class MaintenanceRecordCreate(MaintenanceRecordBase):
    """Payload for creating a maintenance record — needs the owning vehicle's id."""

    vehicle_id: int


class MaintenanceRecordResponse(MaintenanceRecordBase):
    """What we return to the client — adds id and vehicle_id."""

    id: int
    vehicle_id: int
