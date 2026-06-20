from enum import Enum


class MaintenanceType(str, Enum):
    """The fixed set of maintenance categories the API will accept.

    Inheriting from both `str` and `Enum` means each member behaves like a
    normal string at runtime (so it serializes cleanly to JSON) while still
    being restricted to one of the listed values.
    """

    OIL_CHANGE = "Oil Change"
    TIRE_ROTATION = "Tire Rotation"
    BRAKE_SERVICE = "Brake Service"
    BATTERY_REPLACEMENT = "Battery Replacement"
    ENGINE_TUNE_UP = "Engine Tune-Up"
    AIR_FILTER_REPLACEMENT = "Air Filter Replacement"
    GENERAL_INSPECTION = "General Inspection"
    OTHER = "Other"


class FuelType(str, Enum):
    """The fixed set of fuel types a vehicle can run on."""

    PETROL = "Petrol"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"
