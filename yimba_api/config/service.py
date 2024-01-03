from pydantic import Field, HttpUrl

from yimba_api.config import APIBaseSettings


class Auth(APIBaseSettings):
    port: int = Field(..., env="AUTH_PORT")
    host: str = Field(..., env="AUTH_HOST")
    url: HttpUrl = Field(..., env="AUTH_BASE_URL")
    docs_url: str = "/api/auth/docs"
    title: str = "Yimba API :: Auth Service"
    openapi_url: str = "/api/auth/openapi.json"


def get(name: str) -> APIBaseSettings:
    match name:
        case "auth":
            return Auth()
        case _:
            return
