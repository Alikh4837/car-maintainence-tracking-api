from enum import Enum


class MaintenanceType(str, Enum):
    OIL_CHANGE = "Oil Change"
    TIRE_ROTATION = "Tire Rotation"
    BRAKE_SERVICE = "Brake Service"
    BATTERY_REPLACEMENT = "Battery Replacement"
    ENGINE_TUNE_UP = "Engine Tune-Up"
    AIR_FILTER_REPLACEMENT = "Air Filter Replacement"
    GENERAL_INSPECTION = "General Inspection"
    OTHER = "Other"

    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive matching for incoming values."""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class FuelType(str, Enum):
    PETROL = "Petrol"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"

    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive matching for incoming values."""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None