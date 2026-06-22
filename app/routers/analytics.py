from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from app.database.session import get_db
from app.models.enums import MaintenanceType
from app.models.maintainence import MaintenanceRecord
from app.models.vehicle import Vehicle

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class CostByType(BaseModel):
    maintenance_type: MaintenanceType
    total_cost: float
    record_count: int
    average_cost: float


class CostAnalyticsResponse(BaseModel):
    vehicle_id: int
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    license_plate: str
    total_spent: float
    total_services: int
    average_cost_per_service: float
    most_expensive_service: float
    cheapest_service: float
    cost_by_type: list[CostByType]


@router.get("/vehicles/{vehicle_id}/costs", response_model=CostAnalyticsResponse)
def get_vehicle_cost_analytics(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns a full cost breakdown for a vehicle — total spend,
    average, most/least expensive, and a per-type breakdown.
    """
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    records = db.exec(
        select(MaintenanceRecord).where(MaintenanceRecord.vehicle_id == vehicle_id)
    ).all()

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No maintenance records found for this vehicle",
        )

    total_spent = sum(r.cost for r in records)
    total_services = len(records)
    average_cost = total_spent / total_services
    most_expensive = max(r.cost for r in records)
    cheapest = min(r.cost for r in records)

    # Group costs by maintenance type
    type_map: dict[MaintenanceType, list[float]] = {}
    for record in records:
        type_map.setdefault(record.maintenance_type, []).append(record.cost)

    cost_by_type = [
        CostByType(
            maintenance_type=mtype,
            total_cost=sum(costs),
            record_count=len(costs),
            average_cost=sum(costs) / len(costs),
        )
        for mtype, costs in sorted(
            type_map.items(), key=lambda x: sum(x[1]), reverse=True
        )
    ]

    return CostAnalyticsResponse(
        vehicle_id=vehicle.id or 0,
        vehicle_make=vehicle.make,
        vehicle_model=vehicle.model,
        vehicle_year=vehicle.year,
        license_plate=vehicle.license_plate,
        total_spent=round(total_spent, 2),
        total_services=total_services,
        average_cost_per_service=round(average_cost, 2),
        most_expensive_service=most_expensive,
        cheapest_service=cheapest,
        cost_by_type=cost_by_type,
    )


@router.get("/costs/summary", response_model=list[CostAnalyticsResponse])
def get_all_vehicles_cost_summary(
    db: Session = Depends(get_db),
):
    """
    Returns cost analytics for every vehicle that has at least
    one maintenance record — useful for a fleet-wide overview.
    """
    vehicles = db.exec(select(Vehicle)).all()

    result = []
    for vehicle in vehicles:
        records = db.exec(
            select(MaintenanceRecord).where(MaintenanceRecord.vehicle_id == vehicle.id)
        ).all()

        if not records:
            continue

        total_spent = sum(r.cost for r in records)
        total_services = len(records)
        average_cost = total_spent / total_services

        type_map: dict[MaintenanceType, list[float]] = {}
        for record in records:
            type_map.setdefault(record.maintenance_type, []).append(record.cost)

        cost_by_type = [
            CostByType(
                maintenance_type=mtype,
                total_cost=sum(costs),
                record_count=len(costs),
                average_cost=sum(costs) / len(costs),
            )
            for mtype, costs in sorted(
                type_map.items(), key=lambda x: sum(x[1]), reverse=True
            )
        ]

        result.append(
            CostAnalyticsResponse(
                vehicle_id=vehicle.id or 0,
                vehicle_make=vehicle.make,
                vehicle_model=vehicle.model,
                vehicle_year=vehicle.year,
                license_plate=vehicle.license_plate,
                total_spent=round(total_spent, 2),
                total_services=total_services,
                average_cost_per_service=round(average_cost, 2),
                most_expensive_service=max(r.cost for r in records),
                cheapest_service=min(r.cost for r in records),
                cost_by_type=cost_by_type,
            )
        )
    return result
