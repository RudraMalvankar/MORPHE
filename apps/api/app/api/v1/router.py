from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.modules.auth.router import router as auth_router
from app.modules.ingestion.router import router as ingestion_router
from app.modules.nlp.router import router as nlp_router
from app.modules.storage.router import router as storage_router

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(storage_router)
api_v1_router.include_router(ingestion_router)
api_v1_router.include_router(nlp_router)
