import logging
from typing import Annotated

import httpx
from fastapi import Header, status

from src.common.helpers.error_codes import AppErrorCode
from src.common.helpers.exceptions import CustomHTTException
from .url_patterns import CHECK_USERINFO_URL

_log = logging.getLogger(__name__)


class CheckUserInfoHandler:
    """
    Handler to verify access token.
    """

    def __init__(self):
        self.url = CHECK_USERINFO_URL

    async def __call__(self, authorization: Annotated[str, Header(...)]):
        token = authorization.split()[1]

        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, params={"token": token})

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            _log.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            raise CustomHTTException(
                code_error=AppErrorCode.AUTH_ACCESS_DENIED,
                message_error="Access denied",
                status_code=status.HTTP_403_FORBIDDEN,
            ) from exc

        ret = response.json()["active"] if response.is_success else False
        if ret is False:
            raise CustomHTTException(
                code_error=AppErrorCode.AUTH_ACCESS_DENIED,
                message_error="Access denied",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return response.json()
