import logging
from typing import Optional

from fastapi import Body, Query, Security, status
from fastapi_pagination import paginate

from yimba_api.shared import crud
from yimba_api.services import router_factory
from yimba_api.services.analyse import model
from yimba_api.shared.authentication import AuthTokenBearer

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/api/analyse",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/",
    response_model=crud.CustomPage[model.AnalyseInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get all analyse sentiments by posts",
    status_code=status.HTTP_200_OK,
)
async def get_post_sentiments(
    query: Optional[str] = Query(None, alias="search", description="Search by post ID")
):
    analyses = model.AnalyseInDB.find(
        router.storage, {"post_id": query} if query else {}
    )
    result = paginate([item async for item in analyses])
    return result


@router.post(
    "/",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Analyse post sentiments",
    status_code=status.HTTP_201_CREATED,
)
async def analyse_post_sentiments(payload: model.Analyse = Body(...)):
    result = await crud.post(router.storage, model.AnalyseInDB, payload)
    return result


@router.get(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get single analyse post sentiment",
    status_code=status.HTTP_200_OK,
)
async def get_analyse(id: str):
    result = await crud.get(
        router.storage, model.AnalyseInDB, id, f"Analyse with ID '{id}'"
    )
    return result


@router.delete(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Delete analyse post sentiment",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_analyse(id: str):
    result = await crud.delete(router.storage, model.AnalyseInDB, id)
    return result
