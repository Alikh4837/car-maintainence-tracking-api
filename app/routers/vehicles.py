from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, col

from app.database.session import get_db
from app.models.enums import FuelType
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    new_vehicle = Vehicle(**vehicle.model_dump())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(
    make: Optional[str] = Query(default=None, description="Filter by make e.g. Toyota"),
    year: Optional[int] = Query(default=None, description="Filter by manufacture year"),
    fuel_type: Optional[FuelType] = Query(
        default=None, description="Filter by fuel type"
    ),
    include_records: bool = Query(
        default=False, description="Include maintenance history for each vehicle"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
):
    query = select(Vehicle)

    if make:
        query = query.where(col(Vehicle.make).ilike(f"%{make}%"))
    if year:
        query = query.where(Vehicle.year == year)
    if fuel_type:
        query = query.where(Vehicle.fuel_type == fuel_type)

    query = query.offset(offset).limit(limit)
    vehicles = db.exec(query).all()

    if not include_records:
        return [
            {**vehicle.model_dump(), "maintenance_records": []} for vehicle in vehicles
        ]

    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def patch_vehicle(
    vehicle_id: int, vehicle_data: VehicleUpdate, db: Session = Depends(get_db)
):
    """Partially update a vehicle — only the fields you send will change."""
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # exclude_unset=True means fields the caller didn't send are ignored entirely
    updates = vehicle_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(vehicle, field, value)

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}
