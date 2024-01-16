import logging
from typing import Optional

from fastapi.responses import JSONResponse
from fastapi import HTTPException, Query, Security, status
from fastapi_pagination import paginate

from slugify import slugify
from yimba_api.services import router_factory
from yimba_api.services.facebook import model
from yimba_api.shared import crud, scrapper, service
from yimba_api.shared.authentication import AuthTokenBearer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()


router = router_factory(
    prefix="/api/facebook",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/",
    response_model=crud.CustomPage[model.FacebookInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Search facebook by hashtag",
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
        items = model.FacebookInDB.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [
            {"data.hashtag": {"$regex": term, "$options": "i"}} for term in search_terms
        ]
        + [{"data.text": {"$regex": term, "$options": "i"}} for term in search_terms]
        + [{"data.postId": {"$regex": term, "$options": "i"}} for term in search_terms]
    }
    items = model.FacebookInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}", summary="Get facebook hashtag", status_code=status.HTTP_200_OK
)
async def get_facebook_hashtag(
    keyword: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    """
    Extrayez des données de centaines de posts Facebook en utilisant un ou plusieurs hashtags.
    Obtenez le texte et l'URL de la publication, l'heure de la publication, les informations
    de base sur la publication, les URL des images et des vidéos, le texte OCR, le nombre de likes,
    de commentaires et de partages, et bien plus encore.
    """
    try:
        scraping = await scrapper.scrapping_facebook_data(keyword)
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err

    for data in scraping:
        if post := model.FacebookInDB.find_one(
            router.storage, {"data.postId": data.get("postId")}
        ):
            logger.info(f"Object with postId {post.id} already exists. Skipping.")
            continue

        result = await model.FacebookInDB(data=data).save(router.storage)
        response = await crud.get(
            router.storage, model.FacebookInDB, result.inserted_id
        )
        apc = analyzer.polarity_scores(response.data.get("text"))
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
    summary="Remove Facebook information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_facebook_information(id: str):
    return await crud.delete(router.storage, model.FacebookInDB, id)
