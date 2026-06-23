from typing import List, Optional, TYPE_CHECKING, ClassVar

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.maintainence import MaintenanceRecord


class ServiceProviderBase(SQLModel):
    name: str = Field(index=True)
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None  # e.g. "Tires", "Engine", "General"


class ServiceProvider(ServiceProviderBase, table=True):
    __tablename__: ClassVar[str] = "service_provider"

    id: Optional[int] = Field(default=None, primary_key=True)
    maintenance_records: List["MaintenanceRecord"] = Relationship(
        back_populates="provider"
    )