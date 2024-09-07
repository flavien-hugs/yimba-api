from enum import StrEnum
from functools import lru_cache

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class YimbaBaseSettings(BaseSettings):
    APP_ENV: str = Field("DEV", alias="APP_ENV")

    # AUTH ENDPOINT CONFIG
    API_AUTH_URL_BASE: str = Field(..., alias="PERMS_DB_COLLECTION")
    API_AUTH_CHECK_ACCESS_ENDPOINT: str = Field(..., alias="API_AUTH_CHECK_ACCESS_ENDPOINT")

    # MONGODB CONFIG
    PERMS_DB_COLLECTION: str = Field(..., alias="PERMS_DB_COLLECTION")
    APP_DESC_DB_COLLECTION: str = Field(..., alias="APP_DESC_DB_COLLECTION")

    MONGO_DB: str = Field(..., alias="MONGO_DB")
    MONGODB_URI: str = Field(..., alias="MONGODB_URI")
    MONGO_PORT: PositiveInt = Field(..., alias="MONGO_PORT")
    MONGO_USER: str = Field(..., alias="MONGO_USER")
    MONGO_PASSWORD: str = Field(..., alias="MONGO_PASSWORD")


class APIBaseSettings(YimbaBaseSettings):
    API_PORT: PositiveInt = Field(default=9090, alias="API_PORT")
    API_IP_ADDRESS: str = Field(default="0.0.0.0", alias="API_IP_ADDRESS")
    UVICORN_WORKERS: PositiveInt = Field(default=2, alias="UVICORN_WORKERS")


@lru_cache
def base_settings() -> APIBaseSettings:
    return APIBaseSettings()


settings = base_settings()
