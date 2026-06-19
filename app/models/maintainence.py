from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

from app.database.connection import Base


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    maintenance_type = Column(String)
    service_date = Column(Date)
    cost = Column(Float)