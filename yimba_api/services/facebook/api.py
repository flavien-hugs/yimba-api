import logging
from typing import Optional

from fastapi import HTTPException, Query, Security, status
from fastapi_pagination import paginate

from slugify import slugify
from yimba_api.services import router_factory
from yimba_api.services.facebook import model
from yimba_api.shared import crud, scrapper
from yimba_api.shared.authentication import AuthTokenBearer

logger = logging.getLogger(__name__)

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
)
async def search(
    query: Optional[str] = Query(
        None,
        alias="search",
        description="Search by items: hashtag, text",
    )
):
    if query is None:
        return paginate([])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [
            {"data.hashtag": {"$regex": term, "$options": "i"}} for term in search_terms
        ]
        + [{"data.text": {"$regex": term, "$options": "i"}} for term in search_terms]
    }
    items = model.FacebookInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Get facebook hashtag",
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
    result = await model.FacebookInDB(data=scraping).save(router.storage)
    response = await crud.get(router.storage, model.FacebookInDB, result.inserted_id)
    return response


@router.delete(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Remove Facebook information",
)
async def delete_facebook_information(id: str):
    return await crud.delete(router.storage, model.FacebookInDB, id)
