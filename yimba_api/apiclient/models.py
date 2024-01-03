from enum import Enum

from httpx._models import (  # noqa: F401
    ByteStream,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)


class HttpVerbs(str, Enum):
    get: str = "GET"
    head: str = "HEAD"
    post: str = "POST"
    put: str = "PUT"
    delete: str = "DELETE"
    connect: str = "CONNECT"
    options: str = "OPTIONS"
    trace: str = "TRACE"
    patch: str = "PATCH"
