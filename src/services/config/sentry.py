from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class SentrySettings(BaseSettings):
    SENTRY_DSN: str = Field(..., alias="SENTRY_DSN")
    SENTRY_RELEASE: str = Field(..., alias="SENTRY_RELEASE")
    SENTRY_ENVIRONMENT: str = Field(..., alias="SENTRY_ENVIRONMENT")


@lru_cache
def sentry_settings() -> SentrySettings:
    return SentrySettings()


settings = sentry_settings()
