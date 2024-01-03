import typing

import httpx

from yimba_api.apiclient.encoder import jsonable_encoder
from yimba_api.apiclient.models import (
    ByteStream,
    CookieTypes,
    HeaderTypes,
    HttpVerbs,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
)


class ApiClient:
    def __init__(self, baseUrl: str = None) -> None:
        self.baseUrl = (baseUrl or "").strip("/")
        self.headers: HeaderTypes = dict()
        self.auth: typing.Tuple[
            typing.Union[str, bytes], typing.Union[str, bytes]
        ] = None

    def create_request_object(
        self,
        method: HttpVerbs,
        path: str,
        *,
        url: str = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json_data: typing.Any = None,
        stream: ByteStream = None,
        **extra,
    ) -> httpx.Request:
        request_config = {
            "params": params,
            "headers": {**(self.headers or {}), **(headers or {})},
            "cookies": cookies,
            "content": content,
            "data": data,
            "files": files,
            "json": jsonable_encoder(json_data)
            if isinstance(json_data, (dict, list))
            else json_data,
            "stream": stream,
        }
        request = httpx.Request(
            method.upper(),
            (url or f"{self.baseUrl}/{path.lstrip('/')}"),
            **{
                **dict(filter(lambda x: x[1], request_config.items())),
                **extra,
            },
        )
        return request

    def request(
        self,
        method: HttpVerbs,
        path: str,
        *,
        url: str = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json_data: typing.Any = None,
        stream: ByteStream = None,
        auth: typing.Tuple[typing.Union[str, bytes], typing.Union[str, bytes]] = None,
        **extra,
    ) -> httpx.Response:
        with httpx.Client() as httpx_client:
            request = self.create_request_object(
                method,
                path,
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                content=content,
                data=data,
                files=files,
                json_data=json_data,
                stream=stream,
                **extra,
            )
            if auth or self.auth:
                response: httpx.Response = httpx_client.send(
                    request, auth=(auth or self.auth)
                )
            response: httpx.Response = httpx_client.send(request)
        return response

    async def aiorequest(
        self,
        method: HttpVerbs,
        path: str,
        *,
        url: str = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json_data: typing.Any = None,
        stream: ByteStream = None,
        auth: typing.Tuple[typing.Union[str, bytes], typing.Union[str, bytes]] = None,
        **extra,
    ) -> httpx.Response:
        async with httpx.AsyncClient() as httpx_client:
            request = self.create_request_object(
                method,
                path,
                url=url,
                params=params,
                headers=headers,
                cookies=cookies,
                content=content,
                data=data,
                files=files,
                json_data=json_data,
                stream=stream,
                **extra,
            )
            if auth or self.auth:
                response: httpx.Response = await httpx_client.send(
                    request, auth=(auth or self.auth)
                )
            response: httpx.Response = await httpx_client.send(request)
        return response


if __name__ == "__main__":
    import asyncio

    client = ApiClient("https://jsonplaceholder.typicode.com/todos/")
    r = client.request("get", "/")
    a = asyncio.run(client.aiorequest("get", "/"))
