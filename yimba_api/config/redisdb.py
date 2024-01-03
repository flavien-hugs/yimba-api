from pydantic import Field

from yimba_api.config import YimbaBaseSettings


class RedisSettings(YimbaBaseSettings):
    host: str = Field(..., env="REDIS_HOST")
    port: int = Field(..., env="REDIS_PORT")
    password: str = Field(..., env="REDIS_PASSWORD")
    log_level: str = Field(..., env="REDIS_LOG_LEVEL")


settings = RedisSettings()
