from typing import Optional

from starlette import status
from fastapi import Security, Body, Query
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate

from yimba_api.shared import crud
from yimba_api.services import router_factory
from yimba_api.services.project import model

from yimba_api.shared.authentication import AuthTokenBearer, decode_access_token

router = router_factory(
    prefix="/api/project",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.post(
    "/",
    summary="Create new project",
)
async def create_project(
    payload: model.Project = Body(...),
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    result = None
    payload_user = decode_access_token(current_user)
    for key in payload.name.split(","):
        hashtag = key.strip()
        if hashtag:
            result = await model.ProjectInDB(
                name=hashtag, user_id=payload_user.sub
            ).save(router.storage)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "oid": result.inserted_id if result else None,
            "acknowledged": result.acknowledged if result else None,
            "inserted_id": result.inserted_id if result else None,
        },
    )


@router.get(
    "/",
    response_model=crud.CustomPage[model.ProjectInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get all projects",
)
async def get_projects(
    query: Optional[str] = Query(
        default=None, alias="search", description="Search Project by User ID"
    )
):
    filter = (
        {
            "$or": [
                {"user_id": {"$regex": query, "$options": "i"}},
                {"name": {"$regex": query, "$options": "i"}},
            ]
        }
        if query
        else {}
    )
    items = model.ProjectInDB.find(router.storage, filter if query else {})
    result = paginate([item async for item in items])
    return result


@router.get(
    "/by-slug/{slug}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get single project by slug",
)
async def get_project_by_slug(slug: str = None):
    items = model.ProjectInDB.find(router.storage, {"slug": slug} if slug else {})
    result = [{"key": x.slug, "value": x.name} async for x in items]
    return result


@router.get(
    "/{project_id}",
    response_model=model.ProjectInDB,
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get single project",
)
async def get_project(project_id: str):
    return await crud.get(
        router.storage, model.ProjectInDB, project_id, name=f"Project {project_id}"
    )


@router.patch(
    "/{project_id}",
    response_model=model.ProjectInDB,
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Update Project",
)
async def update_project(project_id: str, payload: model.Project = Body(...)):
    return await crud.patch(router.storage, model.ProjectInDB, project_id, payload)


@router.delete(
    "/{project_id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Delete project",
)
async def delete_project(project_id: str):
    return await crud.delete(router.storage, model.ProjectInDB, project_id)
