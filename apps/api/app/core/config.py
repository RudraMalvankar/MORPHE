import os
from typing import List, Union
from pydantic import Field, AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "MORPHE Document Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database Settings
    POSTGRES_USER: str = "morphe_user"
    POSTGRES_PASSWORD: str = "morphe_secret_password"
    POSTGRES_DB: str = "morphe_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://morphe_user:morphe_secret_password@localhost:5432/morphe_db"
    )

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # GROBID Settings
    GROBID_URL: str = "http://localhost:8070"

    # Storage Locations
    ORIGINAL_INPUTS_DIR: str = "storage_data/original"
    CDM_STORAGE_DIR: str = "storage_data/cdm"
    ARTIFACTS_STORAGE_DIR: str = "storage_data/artifacts"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
