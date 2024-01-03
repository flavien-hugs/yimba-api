from enum import Enum

from pydantic import BaseSettings, Field


class LogLevel(str, Enum):
    info: str = "info"
    debug: str = "debug"
    error: str = "error"
    notset: str = "notset"
    warning: str = "warning"
    critical: str = "critical"


class YimbaBaseSettings(BaseSettings):
    env: str = Field("DEV", env="APP_ENV")
    log_level: LogLevel = Field("debug", env="BASE_LOG_LEVEL")

    class Config:
        env_file_encoding = "utf-8"
        env_file = "dotenv/dev.env"


class APIBaseSettings(YimbaBaseSettings):
    port: int = Field(9090, env="API_PORT")
    ip: str = Field(..., env="API_IP_ADDRESS")
    workers: int = Field(2, env="UVICORN_WORKERS")
