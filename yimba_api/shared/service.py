import httpx
from typing import Optional, List
from starlette import status
from pydantic import HttpUrl
from fastapi import HTTPException, Security

from yimba_api.config import service as config_service
from yimba_api.shared.authentication import AuthTokenBearer

AUTH_CONFIG: config_service.Auth = config_service.get("auth")
PARAMS_CONFIG: config_service.Params = config_service.get("params")
PROJECT_CONFIG: config_service.Project = config_service.get("project")


async def validate_resource_exist(
    resource_id: str,
    resource_url: HttpUrl,
    allowed_roles: List[str],
    path: Optional[str] = None,
    current_user: str = None,
) -> str:
    full_url = (
        f"{resource_url}/{path}/{resource_id}"
        if path
        else f"{resource_url}/{resource_id}"
    )
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


async def validate_user_exist(
    user_id: str,
    current_user: str = Security(
        AuthTokenBearer(allowed_role=["admin", "client"]),
        use_cache=True,
    ),
) -> str:
    return await validate_resource_exist(
        resource_id=user_id,
        resource_url=AUTH_CONFIG.url,
        allowed_roles=["admin", "client"],
        current_user=current_user,
    )


async def fetch_resource_data(url: HttpUrl, headers: str = None) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(url, headers=headers)


async def follow_redirects(
    client: httpx.AsyncClient, url: HttpUrl, headers: str
) -> httpx.Response:
    response = await fetch_resource_data(url, headers)
    if (
        status.HTTP_300_MULTIPLE_CHOICES
        <= response.status_code
        < status.HTTP_400_BAD_REQUEST
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


async def validate_roles_exist(
    slug: str,
    current_user: str = Security(
        AuthTokenBearer(allowed_role=["admin", "client"]), use_cache=True
    ),
) -> str:
    return await validate_slug_exist(
        path="roles",
        slug=slug,
        current_user=current_user,
        resource_url=PARAMS_CONFIG.url,
        allowed_roles=["admin", "client"],
        error_message=f"Role '{slug}' not found.",
    )


async def validate_project_exist(
    slug: str,
    current_user: str = Security(
        AuthTokenBearer(allowed_role=["admin", "client"]), use_cache=True
    ),
) -> str:
    return await validate_slug_exist(
        path="by-slug",
        slug=slug,
        current_user=current_user,
        resource_url=PROJECT_CONFIG.url,
        allowed_roles=["admin", "client"],
        error_message=f"Project '{slug}' not found.",
    )
