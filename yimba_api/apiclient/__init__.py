import urllib
from functools import partialmethod

import httpx

from yimba_api.apiclient.core import ApiClient


def is_valid_url(url: str):
    url = urllib.parse.urlparse(url)
    return all((url.scheme, url.netloc))


class Fetch(ApiClient):
    def __call__(
        self, method, url, json=None, raise_for_status=False, **kwargs
    ) -> httpx.Response:
        result = self.request(method, None, url=url, json_data=json, **kwargs)
        if raise_for_status:
            result.raise_for_status()
        return result

    get = partialmethod(__call__, "get")
    post = partialmethod(__call__, "post")
    put = partialmethod(__call__, "put")
    delete = partialmethod(__call__, "delete")
    patch = partialmethod(__call__, "patch")


class AIOFetch(Fetch):
    async def __call__(
        self, method, url, json=None, raise_for_status=False, **kwargs
    ) -> httpx.Response:
        result = await self.aiorequest(method, None, url=url, json_data=json, **kwargs)
        if raise_for_status:
            result.raise_for_status()
        return result

    get = partialmethod(__call__, "get")
    post = partialmethod(__call__, "post")
    put = partialmethod(__call__, "put")
    delete = partialmethod(__call__, "delete")
    patch = partialmethod(__call__, "patch")


fetch = Fetch()
aiofetch = AIOFetch()


if __name__ == "__main__":
    import asyncio

    fr = fetch.get("https://jsonplaceholder.typicode.com/todos/")
    ar = asyncio.run(aiofetch.get("https://jsonplaceholder.typicode.com/todos/"))
