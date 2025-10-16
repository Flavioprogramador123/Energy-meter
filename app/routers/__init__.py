from fastapi import APIRouter
from .clients import router as clients_router
from .devices import router as devices_router
from .ingest import router as ingest_router
from .metrics import router as metrics_router
from .alarms import router as alarms_router
from .dashboard import router as dashboard_router
from ..core.config import settings


def get_api_router() -> APIRouter:
    api = APIRouter()
    api.include_router(clients_router)
    api.include_router(devices_router)
    api.include_router(ingest_router)
    api.include_router(metrics_router)
    api.include_router(alarms_router)
    api.include_router(dashboard_router)
    return api

