from app.models.vehicle import VehicleBase


class VehicleCreate(VehicleBase):
    """Payload for creating/updating a vehicle — same fields as the table, no id."""

    pass


class VehicleResponse(VehicleBase):
    """What we return to the client — adds the generated id."""

    id: int
