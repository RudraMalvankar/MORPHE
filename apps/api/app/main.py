from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.logging import logger
from app.core.redis import close_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} API...")
    yield
    logger.info("Shutting down MORPHE API...")
    await close_redis_client()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health check endpoint
@app.get("/health", tags=["System"])
async def root_health():
    return {"status": "online", "service": "MORPHE API Gateway"}

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
