from pydantic import Field

from yimba_api.config import YimbaBaseSettings


class SentrySettings(YimbaBaseSettings):
    dsn: str = Field(..., env="SENTRY_DSN")
    release: str = Field(..., env="SENTRY_RELEASE")
    environment: str = Field(..., env="SENTRY_ENVIRONMENT")


settings = SentrySettings()
