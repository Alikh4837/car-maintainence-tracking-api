from pydantic import BaseModel, ConfigDict


class VehicleBase(BaseModel):
    make: str
    model: str
    year: int
    license_plate: str


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int