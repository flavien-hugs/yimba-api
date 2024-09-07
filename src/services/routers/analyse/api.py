import logging
from typing import Optional

from fastapi import Body, Depends, Query, status
from fastapi_pagination import paginate

from src.common.helpers.permissions import CheckAccessAllow
from src.services import models, router_factory, schemas
from src.shared import crud
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/analyses",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["analyse:can-make-analyse"]))],
    summary="Create Analyse post sentiments",
    status_code=status.HTTP_201_CREATED,
)
async def analyse_post_sentiments(payload: schemas.CreateAnalyse = Body(...)):
    result = await crud.post(router.storage, models.Analyse, payload.model_dump())
    return result


@router.get(
    "",
    response_model=crud.customize_page(models.Analyse),
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["analyse:can-display-display"]))],
    summary="Get all analyse sentiments by posts",
    status_code=status.HTTP_200_OK,
)
async def get_post_sentiments(query: Optional[str] = Query(None, alias="search", description="Search by post ID")):
    analyses = models.Analyse.find(router.storage, {"post_id": query} if query else {})
    result = paginate([item async for item in analyses])
    return result


@router.get(
    "/{id}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["analyse:can-display-display"]))],
    summary="Get single analyse post sentiment",
    status_code=status.HTTP_200_OK,
)
async def get_analyse(id: str):
    result = await crud.get(router.storage, models.Analyse, id, f"CreateAnalyse with ID '{id}'")
    return result


@router.delete(
    "/{id}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["analyse:can-delete-display"]))],
    summary="Delete analyse post sentiment",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_analyse(id: str):
    result = await crud.delete(router.storage, models.Analyse, id)
    return result
