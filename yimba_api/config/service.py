from pydantic import Field, HttpUrl

from yimba_api.config import APIBaseSettings


class Auth(APIBaseSettings):
    port: int = Field(..., env="AUTH_PORT")
    host: str = Field(..., env="AUTH_HOST")
    url: HttpUrl = Field(..., env="AUTH_BASE_URL")
    docs_url: str = "/api/auth/docs"
    title: str = "Yimba API :: Auth Service"
    openapi_url: str = "/api/auth/openapi.json"


class Params(APIBaseSettings):
    port: int = Field(..., env="PARAMS_PORT")
    host: str = Field(..., env="PARAMS_HOST")
    url: HttpUrl = Field(..., env="PARAMS_BASE_URL")
    docs_url: str = "/api/params/docs"
    title: str = "Yimba API :: Params Service"
    openapi_url: str = "/api/params/openapi.json"


class Project(APIBaseSettings):
    port: int = Field(..., env="PROJECT_PORT")
    host: str = Field(..., env="PROJECT_HOST")
    url: HttpUrl = Field(..., env="PROJECT_BASE_URL")
    docs_url: str = "/api/project/docs"
    title: str = "Yimba API :: Project Service"
    openapi_url: str = "/api/project/openapi.json"


class Facebook(APIBaseSettings):
    port: int = Field(..., env="FACEBOOK_PORT")
    host: str = Field(..., env="FACEBOOK_HOST")
    url: HttpUrl = Field(..., env="FACEBOOK_BASE_URL")
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_facebook_actor: str = Field(..., env="APIFY_FACEBOOK_ACTOR")
    docs_url: str = "/api/facebook/docs"
    title: str = "Yimba API :: Facebook Service"
    openapi_url: str = "/api/facebook/openapi.json"


class Tiktok(APIBaseSettings):
    port: int = Field(..., env="TIKTOK_PORT")
    host: str = Field(..., env="TIKTOK_HOST")
    url: HttpUrl = Field(..., env="TIKTOK_BASE_URL")
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_tiktok_actor: str = Field(..., env="APIFY_TIKTOK_ACTOR")
    docs_url: str = "/api/tiktok/docs"
    title: str = "Yimba API :: Tiktok Service"
    openapi_url: str = "/api/tiktok/openapi.json"


class Twitter(APIBaseSettings):
    port: int = Field(..., env="TWITTER_PORT")
    host: str = Field(..., env="TWITTER_HOST")
    url: HttpUrl = Field(..., env="TWITTER_BASE_URL")
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_twitter_actor: str = Field(..., env="APIFY_TWITTER_ACTOR")
    docs_url: str = "/api/twitter/docs"
    title: str = "Yimba API :: Twitter Service"
    openapi_url: str = "/api/twitter/openapi.json"


class Instagram(APIBaseSettings):
    port: int = Field(..., env="INSTAGRAM_PORT")
    host: str = Field(..., env="INSTAGRAM_HOST")
    url: HttpUrl = Field(..., env="INSTAGRAM_BASE_URL")
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_instagram_actor: str = Field(..., env="APIFY_INSTAGRAM_ACTOR")
    docs_url: str = "/api/instagram/docs"
    title: str = "Yimba API :: Instagram Service"
    openapi_url: str = "/api/instagram/openapi.json"


class Google(APIBaseSettings):
    port: int = Field(..., env="GOOGLE_PORT")
    host: str = Field(..., env="GOOGLE_HOST")
    url: HttpUrl = Field(..., env="GOOGLE_BASE_URL")
    apify_token: str = Field(..., env="APIFY_TOKEN")
    newsapi_key: str = Field(..., env="NEWSAPI_KEY")
    apify_google_actor: str = Field(..., env="APIFY_GOOGLE_ACTOR")
    docs_url: str = "/api/google/docs"
    title: str = "Yimba API :: Google Service"
    openapi_url: str = "/api/google/openapi.json"


class Youtube(APIBaseSettings):
    port: int = Field(..., env="YOUTUBE_PORT")
    host: str = Field(..., env="YOUTUBE_HOST")
    url: HttpUrl = Field(..., env="YOUTUBE_BASE_URL")
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_youtube_actor: str = Field(..., env="APIFY_YOUTUBE_ACTOR")
    docs_url: str = "/api/youtube/docs"
    title: str = "Yimba API :: Youtube Service"
    openapi_url: str = "/api/youtube/openapi.json"


class Statistic(APIBaseSettings):
    port: int = Field(..., env="STATISTIC_PORT")
    host: str = Field(..., env="STATISTIC_HOST")
    url: HttpUrl = Field(..., env="STATISTIC_BASE_URL")
    docs_url: str = "/api/statistics/docs"
    title: str = "Yimba API :: Statistic Service"
    openapi_url: str = "/api/statistics/openapi.json"


class Cloudtags(APIBaseSettings):
    port: int = Field(..., env="CLOUDTAGS_PORT")
    host: str = Field(..., env="CLOUDTAGS_HOST")
    url: HttpUrl = Field(..., env="CLOUDTAGS_BASE_URL")
    docs_url: str = "/api/cloudtags/docs"
    title: str = "Yimba API :: Cloudtags Service"
    openapi_url: str = "/api/cloudtags/openapi.json"


class Analyse(APIBaseSettings):
    port: int = Field(..., env="ANALYSE_PORT")
    host: str = Field(..., env="ANALYSE_HOST")
    url: HttpUrl = Field(..., env="ANALYSE_BASE_URL")
    docs_url: str = "/api/analyse/docs"
    title: str = "Yimba API :: Analyse Service"
    openapi_url: str = "/api/analyse/openapi.json"


def get(name: str) -> APIBaseSettings:
    match name:
        case "auth":
            return Auth()
        case "project":
            return Project()
        case "params":
            return Params()
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
        case "cloudtags":
            return Cloudtags()
        case _:
            return
