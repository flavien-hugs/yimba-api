from typing import Optional

from fastapi import Body, Depends, Query
from fastapi_pagination import paginate

from src.common.helpers.permissions import CheckAccessAllow
from src.services import models, router_factory, schemas
from src.shared import crud
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

router = router_factory(
    prefix="/projects",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-create-project"]))],
    summary="Create new project",
)
async def create_project(payload: schemas.CreateProject = Body(...)):
    pass


@router.get(
    "",
    response_model=crud.customize_page(models.Project),
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-read-project"]))],
    summary="Get all projects",
)
async def get_projects(
        query: Optional[str] = Query(default=None, alias="search", description="Search Project by User ID")
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
    items = models.Project.find(router.storage, filter if query else {})
    result = paginate([item async for item in items])
    return result


@router.get(
    "/{id}",
    response_model=models.Project,
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-read-project"]))],
    summary="Get single project",
)
async def get_project(id: str):
    return await crud.get(router.storage, models.Project, id, name=f"CreateProject {id}")


@router.patch(
    "/{id}",
    response_model=models.Project,
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-update-project"]))],
    summary="Update CreateProject",
)
async def update_project(id: str, payload: schemas.CreateProject = Body(...)):
    return await crud.patch(router.storage, models.Project, id, payload.model_dump())


@router.delete(
    "/{id}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-delete-project"]))],
    summary="Delete project",
)
async def delete_project(id: str):
    return await crud.delete(router.storage, models.Project, id)
