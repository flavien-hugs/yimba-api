from pydantic import Field

from yimba_api.config import YimbaBaseSettings


class ApifyClientSettings(YimbaBaseSettings):
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_actor_id: str = Field(..., env="APIFY_ACTOR_ID")


settings = ApifyClientSettings()
