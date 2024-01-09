import logging
from typing import Optional

from fastapi import HTTPException, Query, Security, status
from fastapi_pagination import paginate

from slugify import slugify
from yimba_api.services.google import model
from yimba_api.services import router_factory
from yimba_api.shared import scrapper, crud
from yimba_api.shared.authentication import AuthTokenBearer

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/api/google",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/",
    response_model=crud.CustomPage[model.GoogleInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Search Google by hashtag",
)
async def search(
    query: Optional[str] = Query(
        None,
        alias="search",
        description="Search by items: hashtag, text",
    )
):
    if query is None:
        items = model.GoogleInDB.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [
            {"data.google.description": {"$regex": term, "$options": "i"}}
            for term in search_terms
        ]
        + [
            {"data.google.title": {"$regex": query, "$options": "i"}}
            for term in search_terms
        ]
        + [
            {"data.newsapi.title": {"$regex": query, "$options": "i"}}
            for term in search_terms
        ]
    }
    items = model.GoogleInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get Google hashtag",
)
async def get_google_hashtag(keyword: str):
    """
    Extraction des pages de résultats des moteurs de recherche Google (SERP).
    Extrayez les résultats organiques et payants, les annonces, les requêtes,
    les personnes qui demandent aussi, les prix, les avis, comme une API SERP de Google.
    """
    try:
        newsapi_data = await scrapper.scrapping_newsapi(keyword)
        google_data = await scrapper.scrapping_google_data(keyword)
        data = {
            "google": google_data[0].get("organicResults", ""),
            "newsapi": newsapi_data,
        }
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err
    result = await model.GoogleInDB(data=data).save(router.storage)
    response = await crud.get(router.storage, model.GoogleInDB, result.inserted_id)
    return response


@router.delete(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Remove Google information",
)
async def delete_google_information(id: str):
    return await crud.delete(router.storage, model.GoogleInDB, id)
