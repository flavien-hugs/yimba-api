from pydantic import Field

from yimba_api.config import YimbaBaseSettings


class ApifyClientSettings(YimbaBaseSettings):
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_google_actor: str = Field(..., env="APIFY_GOOGLE_ACTOR")
    apify_tiktok_actor: str = Field(..., env="APIFY_TIKTOK_ACTOR")
    apify_twitter_actor: str = Field(..., env="APIFY_TWITTER_ACTOR")
    apify_facebook_actor: str = Field(..., env="APIFY_FACEBOOK_ACTOR")
    apify_instagram_actor: str = Field(..., env="APIFY_INSTAGRAM_ACTOR")


settings = ApifyClientSettings()
