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
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_actor_id: str = Field(..., env="APIFY_ACTOR_ID")
    docs_url: str = "/api/project/docs"
    title: str = "Yimba API :: Project Service"
    openapi_url: str = "/api/project/openapi.json"


class Facebook(APIBaseSettings):
    port: int = Field(..., env="FACEBOOK_PORT")
    host: str = Field(..., env="FACEBOOK_HOST")
    url: HttpUrl = Field(..., env="FACEBOOK_BASE_URL")
    apify_token: str = Field(..., env="APIFY_TOKEN")
    apify_actor_id: str = Field(..., env="APIFY_ACTOR_ID")
    docs_url: str = "/api/facebook/docs"
    title: str = "Yimba API :: Facebook Service"
    openapi_url: str = "/api/facebook/openapi.json"


def get(name: str) -> APIBaseSettings:
    match name:
        case "auth":
            return Auth()
        case "project":
            return Project()
        case "params":
            return Params()
        case "facebook":
            return Facebook()
        case _:
            return
