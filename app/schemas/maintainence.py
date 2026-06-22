from datetime import date
from typing import Optional

from app.models.enums import MaintenanceType
from app.models.maintainence import MaintenanceRecordBase
from app.schemas.service_provider import ServiceProviderResponse


class MaintenanceRecordCreate(MaintenanceRecordBase):
    """Payload for creating a maintenance record."""
    vehicle_id: int
    service_provider_id: Optional[int] = None


class MaintenanceRecordUpdate(MaintenanceRecordBase):
    """Payload for partial updates — every field is optional."""
    vehicle_id: Optional[int] = None
    service_provider_id: Optional[int] = None
    maintenance_type: Optional[MaintenanceType] = None
    service_date: Optional[date] = None
    cost: Optional[float] = None
    mileage_at_service: Optional[int] = None
    next_service_due_date: Optional[date] = None
    notes: Optional[str] = None
    warranty_covered: Optional[bool] = None


class MaintenanceRecordResponse(MaintenanceRecordBase):
    """What we return to the client — includes nested provider details."""
    id: int
    vehicle_id: int
    service_provider_id: Optional[int] = None
    provider: Optional[ServiceProviderResponse] = None