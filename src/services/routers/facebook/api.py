import logging
from typing import Optional

from fastapi import BackgroundTasks, Depends, HTTPException, Query, status
from fastapi_pagination import paginate
from pydantic import PositiveInt, ValidationError

from src.common.helpers.exceptions import CustomHTTException
from src.common.helpers.permissions import CheckAccessAllow
from src.services import router_factory, schemas
from src.shared import crud, utils
from src.shared.auth_handler import CheckUserInfoHandler
from src.shared.error_codes import YimbaApifyErrorCode
from src.shared.scrapper import scraper
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)


router = router_factory(
    prefix="/facebook",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


async def fetch_facebook_data(keyword: str, size: Optional[PositiveInt] = 10):
    try:
        result = await scraper.scrape_facebook(keyword=keyword, results_limit=size)
    except HTTPException as exc:
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.BAD_REQUEST, message_error=str(exc), status_code=status.HTTP_400_BAD_REQUEST
        ) from exc

    return result


@router.get(
    "",
    response_model=crud.customize_page(schemas.FacebookResponse),
    dependencies=[
        Depends(
            CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["facebook:can-extract-data-from-facebook-posts"])
        )
    ],
    summary="Get Facebook hashtag",
    status_code=status.HTTP_200_OK,
)
async def all(
    bg: BackgroundTasks,
    keyword: str = Query(),
    user_info: dict = Depends(CheckUserInfoHandler()),
    size: Optional[PositiveInt] = Query(10, description="Number of results per page"),
):
    user = user_info.get("user_info", {}).get("_id")
    await utils.validate_project(keyword, user)

    result = await fetch_facebook_data(keyword, size)

    valid_response = []
    model_fields = set(schemas.FacebookResponse.model_fields)

    for data in result:
        post_id = data.get("postId")
        text = data.get("text", "")
        await utils.analyze_data(bg, post_id, text)
        filtered_item = {k: v for k, v in data.items() if k in model_fields}
        try:
            mention = schemas.FacebookResponse(**filtered_item)
            valid_response.append(mention)
        except ValidationError:
            continue

    return paginate(valid_response)


@router.get(
    "/{keyword}/statistics",
    dependencies=[
        Depends(
            CheckAccessAllow(
                url=CHECK_ACCESS_ALLOW_URL, permissions=["facebook:can-read-scrapper-facebook-data-statistics"]
            )
        )
    ],
    response_model=schemas.CollectStatistic,
    summary="Get facebook scrapper data statictics",
    status_code=status.HTTP_200_OK,
)
async def calculate_stat(keyword: str, size: Optional[PositiveInt] = Query(10)):
    await utils.validate_project(keyword)

    result = await fetch_facebook_data(keyword, size)

    totals = {"likesCount": 0, "sharesCount": 0, "viewsCount": 0, "commentsCount": 0}

    for x in result:
        totals["likesCount"] += x.get("likesCount", 0)
        totals["sharesCount"] += x.get("sharesCount", 0)
        totals["viewsCount"] += x.get("viewsCount", 0)
        totals["commentsCount"] += x.get("commentsCount", 0)

    return schemas.CollectStatistic(**totals)
