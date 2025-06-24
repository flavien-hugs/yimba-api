import logging
from typing import Optional

from fastapi import BackgroundTasks, Depends, HTTPException, Query, status
from fastapi_pagination import paginate
from pydantic import PositiveInt

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
    prefix="/youtube",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


async def fetch_youtube_data(keyword: str, size: Optional[PositiveInt] = 10):
    try:
        result = await scraper.scrape_youtube(keyword=keyword, max_results=size)
    except HTTPException as exc:
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.BAD_REQUEST, message_error=str(exc), status_code=status.HTTP_400_BAD_REQUEST
        ) from exc

    return result


@router.get(
    "",
    response_model=crud.customize_page(dict),
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["youtube:can-display-youtube-data"]))
    ],
    summary="Search youtube by hashtag",
    status_code=status.HTTP_200_OK,
)
async def search(
    bg: BackgroundTasks,
    keyword: str = Query(),
    user_info: dict = Depends(CheckUserInfoHandler()),
    size: Optional[PositiveInt] = Query(10, description="Number of results per page"),
):
    user = user_info.get("user_info", {}).get("_id")
    await utils.validate_project(keyword, user)

    result = await fetch_youtube_data(keyword, size)

    for data in result:
        post_id = data.get("id")
        text = data.get("text", "")
        await utils.analyze_data(bg, post_id, text)

    return paginate(result)


@router.get(
    "/{keyword}/statistics",
    dependencies=[
        Depends(
            CheckAccessAllow(
                url=CHECK_ACCESS_ALLOW_URL, permissions=["youtube:can-read-scrapper-youtube-data-statistics"]
            )
        )
    ],
    response_model=schemas.CollectStatistic,
    summary="Get Youtube scrapper data statictics",
    status_code=status.HTTP_200_OK,
)
async def statistic(keyword: str, size: Optional[PositiveInt] = Query(10)):
    await utils.validate_project(keyword)

    result = await fetch_youtube_data(keyword, size)

    totals = {"likesCount": 0, "sharesCount": 0, "viewsCount": 0, "commentsCount": 0}

    for x in result:
        totals["likesCount"] += x.get("likes", 0)
        totals["sharesCount"] += x.get("shareCount", 0)
        totals["viewsCount"] += x.get("viewCount", 0)
        totals["commentsCount"] += x.get("commentsCount", 0)

    return schemas.CollectStatistic(**totals)
