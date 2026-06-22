from typing import Optional

from app.models.service_provider import ServiceProviderBase


class ServiceProviderCreate(ServiceProviderBase):
    """Payload for creating a service provider."""

    pass


class ServiceProviderUpdate(ServiceProviderBase):
    """Payload for partial updates — every field is optional."""

    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None


class ServiceProviderResponse(ServiceProviderBase):
    """What we return to the client."""

    id: int
