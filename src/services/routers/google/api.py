import logging
from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate
from slugify import slugify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.common.helpers.permissions import CheckAccessAllow
from src.services import models, router_factory
from src.shared import crud, scrapper
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

router = router_factory(
    prefix="/google",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=crud.customize_page(models.Google),
    dependencies=[Depends(
        CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["google:google:can-display-data-from-google"]))],
    summary="Search Colllect Google Data by hashtag",
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
        items = models.Google.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [{"data.description": {"$regex": term, "$options": "i"}} for term in search_terms]
        + [{"data.title": {"$regex": query, "$options": "i"}} for term in search_terms]
    }
    items = models.Google.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL,
                                           permissions=["google:can-extract-data-from-google-search-engine"]))],
    summary="Get google data by hashtag",
    status_code=status.HTTP_200_OK,
)
async def get_google_hashtag(keyword: str):
    """
    Extraction des pages de résultats des moteurs de recherche google (SERP).
    Extrayez les résultats organiques et payants, les annonces, les requêtes,
    les personnes qui demandent aussi, les prix, les avis, comme une API SERP de ColllectGoogleData.
    """
    try:
        google_data = await scrapper.scrapping_google_data(keyword)
        organicresults = google_data[0].get("organicResults", "")
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err

    for data in organicresults:
        apc = analyzer.polarity_scores(data.get("description"))
        result = await models.Google(data=data, analyse=apc).save(router.storage)
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
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL,
                                           permissions=["google:can-delete-data-from-google-search-engine"]))],
    summary="Remove google collect data information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_google_information(id: str):
    return await crud.delete(router.storage, models.Google, id)
