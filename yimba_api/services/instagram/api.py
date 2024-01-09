import logging
from typing import Optional

from fastapi import HTTPException, Query, Security, status
from fastapi_pagination import paginate

from slugify import slugify
from yimba_api.services.instagram import model
from yimba_api.services import router_factory
from yimba_api.shared import scrapper, crud
from yimba_api.shared.authentication import AuthTokenBearer

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/api/instagram",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/",
    response_model=crud.CustomPage[model.InstagramInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Search Instagram by hashtag",
)
async def search(
    query: Optional[str] = Query(
        None,
        alias="search",
        description="Search by items: hashtag, text",
    )
):
    if query is None:
        items = model.InstagramInDB.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [
            {"data.topPosts.hashtags": {"$regex": query, "$options": "i"}}
            for term in search_terms
        ]
        + [
            {"data.latestPosts.hashtags": {"$regex": query, "$options": "i"}}
            for term in search_terms
        ]
        + [
            {"data.searchTerm": {"$regex": query, "$options": "i"}}
            for term in search_terms
        ]
    }
    items = model.InstagramInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get Instagram hashtag",
)
async def get_instagram_hashtag(keyword: str):
    """
    Grattez et téléchargez des posts, profils, lieux, hashtags, photos et commentaires
    Instagram. Obtenez des données d'Instagram à l'aide d'un hashtag Instagram
    ou de requêtes de recherche.
    """
    try:
        data = await scrapper.scrapping_instagram_data(keyword)
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err
    result = await model.InstagramInDB(data=data).save(router.storage)
    response = await crud.get(router.storage, model.InstagramInDB, result.inserted_id)
    return response


@router.delete(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Remove Instagram information",
)
async def delete_instagram_information(id: str):
    return await crud.delete(router.storage, model.InstagramInDB, id)
