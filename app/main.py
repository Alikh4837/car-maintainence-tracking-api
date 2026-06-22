from fastapi import FastAPI

import app.models  # noqa: F401 — registers all models on SQLModel.metadata
from app.routers import alerts, analytics, maintainence, service_provider, vehicles

app = FastAPI(title="Car Maintenance Tracker API")

app.include_router(vehicles.router)
app.include_router(maintainence.router)
app.include_router(service_provider.router)
app.include_router(alerts.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"message": "Car Maintenance Tracker API is running"}
