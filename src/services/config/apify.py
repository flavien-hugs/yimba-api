from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class ApifyClientSettings(BaseSettings):
    APIFY_TOKEN: str = Field(..., alias="APIFY_TOKEN")
    APIFY_GOOGLE_ACTOR: str = Field(..., alias="APIFY_GOOGLE_ACTOR")
    APIFY_TIKTOK_ACTOR: str = Field(..., alias="APIFY_TIKTOK_ACTOR")
    APIFY_TWITTER_ACTOR: str = Field(..., alias="APIFY_TWITTER_ACTOR")
    APIFY_YOUTUBE_ACTOR: str = Field(..., alias="APIFY_YOUTUBE_ACTOR")
    APIFY_FACEBOOK_ACTOR: str = Field(..., alias="APIFY_FACEBOOK_ACTOR")
    APIFY_INSTAGRAM_ACTOR: str = Field(..., alias="APIFY_INSTAGRAM_ACTOR")
    NEWSAPI_KEY: str = Field(..., alias="NEWSAPI_KEY")


@lru_cache
def apify_client_settings() -> ApifyClientSettings:
    return ApifyClientSettings()


settings = apify_client_settings()
