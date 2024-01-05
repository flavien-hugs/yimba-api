from typing import Optional

from fastapi import Query, Security
from fastapi_pagination import paginate

from slugify import slugify
from yimba_api.shared import crud, service
from yimba_api.services import router_factory
from yimba_api.services.facebook import model
from yimba_api.services.facebook import scrapper
from yimba_api.shared.authentication import AuthTokenBearer

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
    response_model=crud.CustomPage[model.Facebook],
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
    search_filter = (
        {
            "$or": [
                {"data.hashtag": {"$regex": query, "$options": "i"}},
                {"data.text": {"$regex": query, "$options": "i"}},
            ]
        }
        if query
        else {}
    )
    items = model.FacebookInDB.find(router.storage, search_filter if query else {})
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    summary="Get facebook hashtag",
)
async def get_facebook_hashtag(
    keyword: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    await service.validate_project_exist(slugify(keyword), current_user)
    scraping = await scrapper.scrapping_facebook_data(keyword)
    result = await model.FacebookInDB(data=scraping).save(router.storage)
    response = await crud.get(router.storage, model.FacebookInDB, result.inserted_id)
    return response
