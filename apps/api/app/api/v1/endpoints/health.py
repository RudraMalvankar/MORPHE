import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime.datetime

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment="development",
        timestamp=datetime.datetime.utcnow()
    )
