from typing import TypeVar, Type

from fastapi import HTTPException
from sqlmodel import Session, SQLModel

from app.models.vehicle import Vehicle

T = TypeVar("T", bound=SQLModel)


def get_or_404(db: Session, model: Type[T], record_id: int) -> T:
    record = db.get(model, record_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"{model.__name__} not found"
        )
    return record


def validate_mileage(mileage_at_service: int, vehicle: Vehicle) -> None:
    """Raises 400 if mileage_at_service exceeds the vehicle's current mileage."""
    if mileage_at_service > vehicle.current_mileage:
        raise HTTPException(
            status_code=400,
            detail=(
                f"mileage_at_service ({mileage_at_service}) cannot exceed "
                f"the vehicle's current mileage ({vehicle.current_mileage}). "
                "Update the vehicle's mileage first if the odometer has advanced."
            ),
        )


def apply_updates(db: Session, instance: T, data, *, exclude_none: bool = False) -> T:
    """Apply a partial update schema to a model instance and commit."""
    updates = data.model_dump(exclude_unset=True, exclude_none=exclude_none)
    for field, value in updates.items():
        setattr(instance, field, value)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance