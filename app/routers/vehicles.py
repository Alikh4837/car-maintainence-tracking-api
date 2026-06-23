from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select, col
from sqlmodel.sql.expression import SelectOfScalar

from app.dependencies.db_helpers import get_or_404, apply_updates
from app.database.session import get_db
from app.dependencies.pagination import PaginationParams, paginate
from app.models.enums import FuelType
from app.models.vehicle import Vehicle
from app.schemas.pagination import PaginatedResponse
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    new_vehicle = Vehicle(**vehicle.model_dump())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle


@router.get("/", response_model=PaginatedResponse[VehicleResponse])
def get_vehicles(
    make: Optional[str] = Query(default=None, description="Filter by make e.g. Toyota"),
    year: Optional[int] = Query(default=None, description="Filter by manufacture year"),
    fuel_type: Optional[FuelType] = Query(
        default=None, description="Filter by fuel type"
    ),
    include_records: bool = Query(
        default=False, description="Include maintenance history for each vehicle"
    ),
    pagination: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db),
):
    data_query: SelectOfScalar[Vehicle] = select(Vehicle)
    count_query: SelectOfScalar[int] = select(func.count()).select_from(Vehicle)

    if make:
        data_query = data_query.where(col(Vehicle.make).ilike(f"%{make}%"))
        count_query = count_query.where(col(Vehicle.make).ilike(f"%{make}%"))
    if year:
        data_query = data_query.where(Vehicle.year == year)
        count_query = count_query.where(Vehicle.year == year)
    if fuel_type:
        data_query = data_query.where(Vehicle.fuel_type == fuel_type)
        count_query = count_query.where(Vehicle.fuel_type == fuel_type)

    result = paginate(db, data_query, count_query, pagination)

    if not include_records:
        return PaginatedResponse(
            items=[
                VehicleResponse(**{**v.model_dump(), "maintenance_records": []})
                for v in result.items
            ],
            total=result.total,
            limit=result.limit,
            offset=result.offset,
        )

    return result


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Vehicle, vehicle_id)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def patch_vehicle(
    vehicle_id: int, vehicle_data: VehicleUpdate, db: Session = Depends(get_db)
):
    """Partially update a vehicle — only the fields you send will change."""
    vehicle = get_or_404(db, Vehicle, vehicle_id)
    return apply_updates(db, vehicle, vehicle_data)


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = get_or_404(db, Vehicle, vehicle_id)

    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}
