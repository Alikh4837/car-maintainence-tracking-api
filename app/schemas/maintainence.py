from datetime import date

from pydantic import BaseModel, ConfigDict


class MaintenanceRecordBase(BaseModel):
    maintenance_type: str
    service_date: date
    cost: float


class MaintenanceRecordCreate(MaintenanceRecordBase):
    vehicle_id: int


class MaintenanceRecordResponse(MaintenanceRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int