from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select

from app.database.session import get_db
from app.models.service_provider import ServiceProvider
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


@router.get("/", response_model=list[ServiceProviderResponse])
def get_service_providers(
    name: Optional[str] = Query(default=None, description="Filter by name"),
    specialization: Optional[str] = Query(
        default=None, description="Filter by specialization"
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(ServiceProvider)
    if name:
        query = query.where(col(ServiceProvider.name).ilike(f"%{name}%"))
    if specialization:
        query = query.where(
            col(ServiceProvider.specialization).ilike(f"%{specialization}%")
        )
    query = query.offset(offset).limit(limit)
    return db.exec(query).all()


@router.get("/{provider_id}", response_model=ServiceProviderResponse)
def get_service_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return provider


@router.patch("/{provider_id}", response_model=ServiceProviderResponse)
def patch_service_provider(
    provider_id: int,
    provider_data: ServiceProviderUpdate,
    db: Session = Depends(get_db),
):
    """Partially update a service provider."""
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")

    updates = provider_data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in updates.items():
        setattr(provider, field, value)

    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/{provider_id}")
def delete_service_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")

    db.delete(provider)
    db.commit()
    return {"message": "Service provider deleted successfully"}
