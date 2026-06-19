from sqlalchemy import Column, Integer, String

from app.database.connection import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    make = Column(String, index=True)
    model = Column(String)
    year = Column(Integer)
    license_plate = Column(String, index=True)