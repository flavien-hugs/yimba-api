import logging
from typing import Optional

from fastapi.responses import JSONResponse
from fastapi import HTTPException, Query, Security, status
from fastapi_pagination import paginate

from slugify import slugify
from yimba_api.services.tiktok import model
from yimba_api.services import router_factory
from yimba_api.shared import scrapper, crud, service
from yimba_api.shared.authentication import AuthTokenBearer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

router = router_factory(
    prefix="/api/tiktok",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/",
    response_model=crud.CustomPage[model.TiktokInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Search Tiktok by hashtag",
    status_code=status.HTTP_200_OK,
)
async def search(
    query: Optional[str] = Query(
        None,
        alias="search",
        description="Search by items: hashtag, text",
    )
):
    if query is None:
        items = model.TiktokInDB.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [{"data.hashtags": {"$regex": query, "$options": "i"}} for term in search_terms]
        + [{"data.text": {"$regex": query, "$options": "i"}} for term in search_terms]
    }
    items = model.TiktokInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get("/{keyword}", summary="Get Tiktok hashtag", status_code=status.HTTP_200_OK)
async def get_tiktok_hashtag(
    keyword: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    """
    Extrayez des données sur les vidéos, les utilisateurs et les chaînes en vous basant
    sur les hashtags ou récupérez les profils complets des utilisateurs, y compris les messages,
    le nombre total de likes, le nom, le surnom, le nombre de commentaires,
    de partages, de followers, de personnes suivies, etc.
    """
    try:
        scraping = await scrapper.scrapping_tiktok_data(keyword)
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err

    for data in scraping:
        apc = analyzer.polarity_scores(data.get("text"))
        result = await model.TiktokInDB(data=data, analyse=apc).save(router.storage)
        await service.analyse_post_text(
            {
                "post_id": result.inserted_id,
                "neutre": apc.get("neu"),
                "negatif": apc.get("neg"),
                "positif": apc.get("pos"),
                "compound": apc.get("compound"),
            },
            current_user,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Scrapping successful!"}
    )


@router.delete(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Remove Tiktok information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tiktok_information(id: str):
    return await crud.delete(router.storage, model.TiktokInDB, id)
