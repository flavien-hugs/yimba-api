import logging
from typing import Optional

from fastapi import HTTPException, Query, Security, status
from fastapi_pagination import paginate

from yimba_api.services.twitter import model
from yimba_api.services import router_factory
from yimba_api.shared import scrapper, crud
from yimba_api.shared.authentication import AuthTokenBearer

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/api/twitter",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/{id}",
    response_model=model.TwitterInDB,
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get Twitter information",
)
async def get_tiktok_information(id: str):
    return await crud.get(
        router.storage, model.TwitterInDB, id, name=f"Twitter Information {id}"
    )


@router.get(
    "/",
    response_model=crud.CustomPage[model.TwitterInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Search Twitter by hashtag",
)
async def search(
    query: Optional[str] = Query(
        None,
        alias="search",
        description="Search by items: hashtag, text",
    )
):
    search_filter = (
        {
            "$or": [
                {"data.hashtags": {"$regex": query, "$options": "i"}},
                {"data.text": {"$regex": query, "$options": "i"}},
            ]
        }
        if query
        else {}
    )
    items = model.TwitterInDB.find(router.storage, search_filter if query else {})
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get Twitter hashtag",
)
async def get_twitter_hashtag(keyword: str):
    """
    Récupérez les tweets de n'importe quel profil d'utilisateur de Twitter.
    Cette API Twitter récupère les hashtags, fils de discussion,
    réponses, followers, images, vidéos, statistiques et l'historique de Twitter.
    """
    try:
        scraping = await scrapper.scrapping_twitter_data(keyword)
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err
    result = await model.TwitterInDB(data=scraping).save(router.storage)
    response = await crud.get(router.storage, model.TwitterInDB, result.inserted_id)
    return response


@router.delete(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Remove Twitter information",
)
async def delete_twitter_information(id: str):
    return await crud.delete(router.storage, model.TwitterInDB, id)
