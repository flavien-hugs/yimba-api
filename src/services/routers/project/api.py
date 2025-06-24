from typing import List, Optional

from beanie import PydanticObjectId
from fastapi import Body, Depends, Query, status
from fastapi_pagination.ext.beanie import paginate
from pymongo import ASCENDING, DESCENDING

from src.common.helpers.error_codes import AppErrorCode
from src.common.helpers.exceptions import CustomHTTException
from src.common.helpers.permissions import CheckAccessAllow
from src.services import models, router_factory, schemas
from src.shared import crud
from src.shared.auth_handler import CheckUserInfoHandler
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL
from src.shared.utils import SortEnum

router = router_factory(
    prefix="/projects",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=List[models.Project],
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-create-project"]))],
    summary="Create new project",
)
async def create(user_info: dict = Depends(CheckUserInfoHandler()), payload: schemas.CreateProject = Body(...)):
    projects = []
    user = user_info.get("user_info", {})
    keywords = [key.strip() for key in payload.name.split(",") if key.strip()]

    if not keywords:
        raise CustomHTTException(
            code_error=AppErrorCode.REQUEST_VALIDATION_ERROR,
            message_error="No valid project names provided",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    for keyword in keywords:
        project = await models.Project(name=keyword, user=user).create()
        projects.append(project)

    return projects


@router.get(
    "",
    response_model=crud.customize_page(models.Project),
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-read-project"]))],
    summary="Get all projects",
)
async def all(
    user_id: Optional[str] = Query(default=None, description="User ID"),
    search: Optional[str] = Query(default=None, description="Search Project by User ID"),
    sort: Optional[SortEnum] = Query(
        SortEnum.DESC,
        description="Order by creation date: 'asc' or 'desc",
    ),
):
    query = {}
    if user_id:
        query["user._id"] = user_id

    if search:
        query["$text"] = {"$search": search}

    sorted = DESCENDING if sort == SortEnum.DESC else ASCENDING
    projects = models.Project.find(query, sort=[("created_at", sorted)])

    return await paginate(projects)


@router.get(
    "/{id}",
    response_model=models.Project,
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-read-project"]))],
    summary="Get single project",
)
async def read(id: PydanticObjectId):
    return await crud.get(models.Project, id=PydanticObjectId(id))


@router.patch(
    "/{id}",
    response_model=models.Project,
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-update-project"]))],
    summary="Update Project",
)
async def update(id: PydanticObjectId, payload: schemas.CreateProject = Body(...)):
    return await crud.patch(models.Project, id=PydanticObjectId(id), payload=payload)


@router.delete(
    "/{id}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["project:can-delete-project"]))],
    summary="Delete project",
)
async def delete(id: PydanticObjectId):
    return await crud.delete(models.Project, id=PydanticObjectId(id))
