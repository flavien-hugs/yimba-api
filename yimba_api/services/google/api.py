import logging
from typing import Optional

from fastapi.responses import JSONResponse
from fastapi import HTTPException, Query, Security, status
from fastapi_pagination import paginate

from slugify import slugify
from yimba_api.services.google import model
from yimba_api.services import router_factory
from yimba_api.shared import scrapper, crud, service
from yimba_api.shared.authentication import AuthTokenBearer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

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
        items = model.GoogleInDB.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [
            {"data.description": {"$regex": term, "$options": "i"}}
            for term in search_terms
        ]
        + [{"data.title": {"$regex": query, "$options": "i"}} for term in search_terms]
    }
    items = model.GoogleInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get("/{keyword}", summary="Get Google hashtag", status_code=status.HTTP_200_OK)
async def get_google_hashtag(
    keyword: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    """
    Extraction des pages de résultats des moteurs de recherche Google (SERP).
    Extrayez les résultats organiques et payants, les annonces, les requêtes,
    les personnes qui demandent aussi, les prix, les avis, comme une API SERP de Google.
    """
    try:
        google_data = await scrapper.scrapping_google_data(keyword)
        organicresults = google_data[0].get("organicResults", "")
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err

    for data in organicresults:
        apc = analyzer.polarity_scores(data.get("description"))
        result = await model.GoogleInDB(data=data, analyse=apc).save(router.storage)
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
    summary="Remove Google information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_google_information(id: str):
    return await crud.delete(router.storage, model.GoogleInDB, id)
