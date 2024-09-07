from typing import cast, List, Optional

import httpx
from fastapi import HTTPException
from pydantic import HttpUrl
from starlette import status

from src.services.config import service as config_service

PROJECT_CONFIG = cast(config_service.Project, config_service.get(name="project"))
ANALYSE_CONFIG = cast(config_service.Analyse, config_service.get(name="analyse"))


async def validate_resource_exist(
    resource_id: str,
    resource_url: HttpUrl,
    allowed_roles: List[str],
    path: Optional[str] = None,
    current_user: str = None,
) -> str:
    full_url = f"{resource_url}/{path}/{resource_id}" if path else f"{resource_url}/{resource_id}"
    headers = {"Authorization": f"Bearer {current_user}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(full_url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"Resource ID {resource_id} does not exist.",
        ) from http_err

    return resource_id


async def fetch_resource_data(url: HttpUrl, headers: str = None) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(url, headers=headers)


async def follow_redirects(client: httpx.AsyncClient, url: HttpUrl, headers: str) -> httpx.Response:
    response = await fetch_resource_data(url, headers)
    if (
        status.HTTP_300_MULTIPLE_CHOICES <= response.status_code < status.HTTP_400_BAD_REQUEST
        and "location" in response.headers
    ):
        new_url = response.headers["location"]
        response = await fetch_resource_data(new_url, headers)
    return response


async def get_json_data(response: httpx.Response) -> dict:
    try:
        response.raise_for_status()
        return response.json()
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error decoding JSON response: {ve}",
        ) from ve


async def validate_slug_exist(
    slug: str,
    resource_url: HttpUrl,
    allowed_roles: List[str],
    path: Optional[str] = None,
    current_user: str = None,
    error_message: str = None,
) -> str:
    full_url = f"{resource_url}/{path}/{slug}" if path else f"{resource_url}/{slug}"
    headers = {"Authorization": f"Bearer {current_user}"}

    try:
        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.get(full_url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as httpx_err:
        raise HTTPException(
            status_code=httpx_err.response.status_code,
            detail=str(httpx_err),
        ) from httpx_err

    if not (response_json := response.json()) or not (
        isinstance(response_json, list) and response_json[0].get("value")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{error_message}",
        )

    return response.json()[0].get("value")


async def analyse_post_text(
    payload: dict,
    current_user: Optional[str] = None,
) -> httpx.Response:
    headers = {"Authorization": f"Bearer {current_user}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ANALYSE_CONFIG.url, json=payload, headers=headers)
            if (
                status.HTTP_300_MULTIPLE_CHOICES <= response.status_code < status.HTTP_400_BAD_REQUEST
                and "location" in response.headers
            ):
                new_url = response.headers["location"]
                response = await client.post(new_url, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=err.response.status_code,
            detail=str(err),
        ) from err
    return response


async def get_counts_data(data_list, key):
    return [x.data.get(key) async for x in data_list]
