import logging
from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate
from slugify import slugify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.common.helpers.permissions import CheckAccessAllow
from src.services import models
from src.services import router_factory
from src.shared import crud, scrapper
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

router = router_factory(
    prefix="/twitter",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=crud.customize_page(models.Twitter),
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["twitter:can-display-twitter-data"]))],
    summary="Search Twitter by hashtag",
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
        items = models.Twitter.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [{"data.hashtags": {"$regex": query, "$options": "i"}} for term in search_terms]
               + [{"data.full_text": {"$regex": query, "$options": "i"}} for term in search_terms]
    }
    items = models.Twitter.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Depends(
        CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["twitter:can-extract-data-from-twitter-posts"]))],
    summary="Get Twitter hashtag",
    status_code=status.HTTP_200_OK,
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err

    for data in scraping:
        apc = analyzer.polarity_scores(data.get("full_text"))
        result = await models.Twitter(data=data, analyse=apc).save(router.storage)
        # await service.analyse_post_text(
        #     {
        #         "post_id": result.inserted_id,
        #         "neutre": apc.get("neu"),
        #         "negatif": apc.get("neg"),
        #         "positif": apc.get("pos"),
        #         "compound": apc.get("compound"),
        #     },
        #     current_user,
        # )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Scrapping successful!"})


@router.delete(
    "/{id}",
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["twitter:can-delete-data-from-twitter"]))],
    summary="Remove Twitter information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_twitter_information(id: str):
    return await crud.delete(router.storage, models.Twitter, id)
