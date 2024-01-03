from functools import partialmethod

import httpx
from pydantic import Field, HttpUrl

from yimba_api import get_logger
from yimba_api.apiclient import ApiClient
from yimba_api.config import YimbaBaseSettings

logger = get_logger("ServiceFetch")


class ServiceBaseUrl(YimbaBaseSettings):
    auth: HttpUrl = Field(..., env="AUTH_BASE_URL")


baseUrl = ServiceBaseUrl()


class ServiceFetch(ApiClient):
    def __init__(self, url: str, name: str) -> None:
        super().__init__(url)
        self.name = name

    async def __call__(
        self, method, path, json=None, raise_for_status=False, **kwargs
    ) -> httpx.Response:
        request_info = {
            "method": method,
            "baseUrl": self.baseUrl,
            "path": path,
            "json_data": json,
            **kwargs,
        }
        logger.info(f"{self.name.upper()} :: {request_info=}")
        result = await self.aiorequest(method, path, json_data=json, **kwargs)
        if not result.is_success:
            logger.warning(f"{self.name.upper()}:: {result}")
        if raise_for_status:
            result.raise_for_status()
        return result

    get = partialmethod(__call__, "get")
    post = partialmethod(__call__, "post")
    put = partialmethod(__call__, "put")
    delete = partialmethod(__call__, "delete")
    patch = partialmethod(__call__, "patch")


auth = ServiceFetch(str(baseUrl.auth), "auth")


if __name__ == "__main__":
    import asyncio

    r = asyncio.run(auth.get("/"))
