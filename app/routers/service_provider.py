from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select, col

from app.database.session import get_db
from app.dependencies.db_helpers import get_or_404, apply_updates
from app.dependencies.pagination import PaginationParams, paginate
from app.models.service_provider import ServiceProvider
from app.schemas.pagination import PaginatedResponse
from app.schemas.service_provider import (
    ServiceProviderCreate,
    ServiceProviderResponse,
    ServiceProviderUpdate,
)

router = APIRouter(prefix="/service-providers", tags=["Service Providers"])


@router.post("/", response_model=ServiceProviderResponse)
def create_service_provider(
    provider: ServiceProviderCreate, db: Session = Depends(get_db)
):
    new_provider = ServiceProvider(**provider.model_dump())
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return new_provider


@router.get("/", response_model=PaginatedResponse[ServiceProviderResponse])
def get_service_providers(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    specialization: Optional[str] = Query(
        default=None, description="Filter by specialization"
    ),
    pagination: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db),
):
    data_query = select(ServiceProvider)
    count_query = select(func.count()).select_from(ServiceProvider)

    if name:
        data_query = data_query.where(col(ServiceProvider.name).ilike(f"%{name}%"))
        count_query = count_query.where(col(ServiceProvider.name).ilike(f"%{name}%"))
    if specialization:
        data_query = data_query.where(
            col(ServiceProvider.specialization).ilike(f"%{specialization}%")
        )
        count_query = count_query.where(
            col(ServiceProvider.specialization).ilike(f"%{specialization}%")
        )

    return paginate(db, data_query, count_query, pagination)


@router.get("/{provider_id}", response_model=ServiceProviderResponse)
def get_service_provider(provider_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, ServiceProvider, provider_id)


@router.patch("/{provider_id}", response_model=ServiceProviderResponse)
def patch_service_provider(
    provider_id: int,
    provider_data: ServiceProviderUpdate,
    db: Session = Depends(get_db),
):
    """Partially update a service provider."""
    provider = get_or_404(db, ServiceProvider, provider_id)
    return apply_updates(db, provider, provider_data, exclude_none=True)


@router.delete("/{provider_id}")
def delete_service_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = get_or_404(db, ServiceProvider, provider_id)
    db.delete(provider)
    db.commit()
    return {"message": "Service provider deleted successfully"}
