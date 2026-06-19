from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401 — registers all models on Base.metadata
from app.database.connection import Base, engine
from app.routers import maintainence, vehicles


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     Base.metadata.create_all(bind=engine)
#     yield


app = FastAPI(title="Car Maintenance Tracker API")

app.include_router(vehicles.router)
app.include_router(maintainence.router)


@app.get("/")
def root():
    return {"message": "Car Maintenance Tracker API is running"}
