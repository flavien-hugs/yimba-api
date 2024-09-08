from pydantic import Field, HttpUrl

from .base import APIBaseSettings


class Project(APIBaseSettings):
    API_PORT: int = Field(..., alias="PROJECT_PORT")
    host: str = Field(..., alias="PROJECT_HOST")
    url: HttpUrl = Field(..., alias="PROJECT_BASE_URL")
    docs_url: str = "/project/docs"
    title: str = "Yimba API :: Project Service"
    openapi_url: str = "/project/openapi.json"


class Facebook(APIBaseSettings):
    API_PORT: int = Field(..., alias="FACEBOOK_PORT")
    APIFY_TOKEN: str = Field(..., alias="APIFY_TOKEN")
    APIFY_FACEBOOK_ACTOR: str = Field(..., alias="APIFY_FACEBOOK_ACTOR")
    host: str = Field(..., alias="FACEBOOK_HOST")
    url: HttpUrl = Field(..., alias="FACEBOOK_BASE_URL")
    docs_url: str = "/facebook/docs"
    title: str = "Yimba API :: Collect Facebook data Service"
    openapi_url: str = "/facebook/openapi.json"


class Tiktok(APIBaseSettings):
    API_PORT: int = Field(..., alias="TIKTOK_PORT")
    APIFY_TOKEN: str = Field(..., alias="APIFY_TOKEN")
    APIFY_TIKTOK_ACTOR: str = Field(..., alias="APIFY_TIKTOK_ACTOR")
    host: str = Field(..., alias="TIKTOK_HOST")
    url: HttpUrl = Field(..., alias="TIKTOK_BASE_URL")
    docs_url: str = "/tiktok/docs"
    title: str = "Yimba API :: Collecte Tiktok data Service"
    openapi_url: str = "/tiktok/openapi.json"


class Twitter(APIBaseSettings):
    API_PORT: int = Field(..., alias="TWITTER_PORT")
    APIFY_TOKEN: str = Field(..., alias="APIFY_TOKEN")
    APIFY_TWITTER_ACTOR: str = Field(..., alias="APIFY_TWITTER_ACTOR")
    host: str = Field(..., alias="TWITTER_HOST")
    url: HttpUrl = Field(..., alias="TWITTER_BASE_URL")
    docs_url: str = "/twitter/docs"
    title: str = "Yimba API :: Collect Twitter data Service"
    openapi_url: str = "/twitter/openapi.json"


class Instagram(APIBaseSettings):
    API_PORT: int = Field(..., alias="INSTAGRAM_PORT")
    APIFY_TOKEN: str = Field(..., alias="APIFY_TOKEN")
    APIFY_INSTAGRAM_ACTOR: str = Field(..., alias="APIFY_INSTAGRAM_ACTOR")
    host: str = Field(..., alias="INSTAGRAM_HOST")
    url: HttpUrl = Field(..., alias="INSTAGRAM_BASE_URL")
    docs_url: str = "/instagram/docs"
    title: str = "Yimba API :: Collect Instagram data Service"
    openapi_url: str = "/instagram/openapi.json"


class Google(APIBaseSettings):
    API_PORT: int = Field(..., alias="GOOGLE_PORT")
    APIFY_TOKEN: str = Field(..., alias="APIFY_TOKEN")
    NEWSAPI_KEY: str = Field(..., alias="NEWSAPI_KEY")
    APIFY_GOOGLE_ACTOR: str = Field(..., alias="APIFY_GOOGLE_ACTOR")
    host: str = Field(..., alias="GOOGLE_HOST")
    url: HttpUrl = Field(..., alias="GOOGLE_BASE_URL")
    docs_url: str = "/google/docs"
    title: str = "Yimba API :: Colllect Google data Service"
    openapi_url: str = "/google/openapi.json"


class Youtube(APIBaseSettings):
    API_PORT: int = Field(..., alias="YOUTUBE_PORT")
    APIFY_TOKEN: str = Field(..., alias="APIFY_TOKEN")
    APIFY_YOUTUBE_ACTOR: str = Field(..., alias="APIFY_YOUTUBE_ACTOR")
    host: str = Field(..., alias="YOUTUBE_HOST")
    url: HttpUrl = Field(..., alias="YOUTUBE_BASE_URL")
    docs_url: str = "/youtube/docs"
    title: str = "Yimba API :: Collect Youtube data Service"
    openapi_url: str = "/youtube/openapi.json"


class Statistic(APIBaseSettings):
    API_PORT: int = Field(..., alias="STATISTIC_PORT")
    host: str = Field(..., alias="STATISTIC_HOST")
    url: HttpUrl = Field(..., alias="STATISTIC_BASE_URL")
    docs_url: str = "/statistics/docs"
    title: str = "Yimba API :: Statistic Service"
    openapi_url: str = "/statistics/openapi.json"


class Cloudtags(APIBaseSettings):
    API_PORT: int = Field(..., alias="CLOUDTAGS_PORT")
    host: str = Field(..., alias="CLOUDTAGS_HOST")
    url: HttpUrl = Field(..., alias="CLOUDTAGS_BASE_URL")
    docs_url: str = "/cloudtags/docs"
    title: str = "Yimba API :: Cloudtags Service"
    openapi_url: str = "/cloudtags/openapi.json"


class Rapport(APIBaseSettings):
    API_PORT: int = Field(..., alias="RAPPORT_PORT")
    host: str = Field(..., alias="RAPPORT_HOST")
    url: HttpUrl = Field(..., alias="RAPPORT_BASE_URL")
    docs_url: str = "/rapport/docs"
    title: str = "Yimba API :: Rapport Service"
    openapi_url: str = "/rapport/openapi.json"


class Analyse(APIBaseSettings):
    API_PORT: int = Field(..., alias="ANALYSE_PORT")
    host: str = Field(..., alias="ANALYSE_HOST")
    url: HttpUrl = Field(..., alias="ANALYSE_BASE_URL")
    docs_url: str = "/analyse/docs"
    title: str = "Yimba API :: Analyse Service"
    openapi_url: str = "/analyse/openapi.json"


def get(name: str) -> APIBaseSettings:
    match name:
        case "project":
            return Project()
        case "google":
            return Google()
        case "tiktok":
            return Tiktok()
        case "twitter":
            return Twitter()
        case "facebook":
            return Facebook()
        case "youtube":
            return Youtube()
        case "instagram":
            return Instagram()
        case "analyse":
            return Analyse()
        case "rapport":
            return Rapport()
        case "cloudtags":
            return Cloudtags()
        case _:
            raise ValueError(f"Unknown API name: {name}")
