from functools import lru_cache

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    SMTP_PORT: PositiveInt = Field(..., alias="SMTP_PORT")
    SMTP_SERVER: str = Field(..., alias="SMTP_SERVER")
    EMAIL_ADDRESS: str = Field(..., alias="EMAIL_ADDRESS")
    EMAIL_PASSWORD: str = Field(..., alias="EMAIL_PASSWORD")


@lru_cache
def email_settings() -> EmailSettings:
    return EmailSettings()


settings = email_settings()
