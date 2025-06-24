from functools import lru_cache

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class YimbaBaseSettings(BaseSettings):
    APP_ENV: str = Field("DEV", alias="APP_ENV")

    # MODELS NAMES CONFIG
    PROJECT_MODEL_NAME: str = Field(..., alias="PROJECT_MODEL_NAME")
    ANALYSE_MODEL_NAME: str = Field(..., alias="ANALYSE_MODEL_NAME")

    # AUTH ENDPOINT CONFIG
    API_AUTH_URL_BASE: str = Field(..., alias="API_AUTH_URL_BASE")
    CHECK_ACCESS_URL: str = Field(..., alias="CHECK_ACCESS_URL")
    CHECK_USERINFO_URL: str = Field(..., alias="CHECK_USERINFO_URL")

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
