import logging
from asyncio import gather
from itertools import chain
from typing import Any, Dict, List, Optional

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
    prefix="/instagram",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


async def fetch_instagram_data(keyword: str, size: Optional[PositiveInt] = 20):
    try:
        result = await scraper.scrape_instagram(keyword=keyword, results_limit=size)
    except HTTPException as exc:
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.BAD_REQUEST, message_error=str(exc), status_code=status.HTTP_400_BAD_REQUEST
        ) from exc

    return result


async def split_data(data: List[Dict[str, Any]], bg: BackgroundTasks) -> List[Dict[str, Any]]:
    async def process_post(post: Dict[str, Any]) -> None:
        post_id = post.get("id")
        text = post.get("caption", "")
        if post_id and text:
            await utils.analyze_data(bg, post_id, text)

    tasks = []
    result_data = []

    for item in data:
        top_posts = item.get("topPosts", [])
        latest_posts = item.get("latestPosts", [])

        posts = list(chain(top_posts, latest_posts))
        result_data.extend(posts)

        tasks.extend(process_post(post) for post in posts)

    await gather(*tasks)

    return result_data


@router.get(
    "",
    response_model=crud.customize_page(dict),
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["instagram:can-extract-data-from-instagram"]))
    ],
    summary="Search instagram data by hashtag",
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

    instagram_data = await fetch_instagram_data(keyword, size)

    result_data = await split_data(instagram_data, bg)

    return paginate(result_data)


@router.get(
    "/{keyword}/statistics",
    dependencies=[
        Depends(
            CheckAccessAllow(
                url=CHECK_ACCESS_ALLOW_URL, permissions=["instagram:can-read-scrapper-instagram-data-statistics"]
            )
        )
    ],
    response_model=schemas.CollectStatistic,
    summary="Get instagram scrapper data statictics",
    status_code=status.HTTP_200_OK,
)
async def statistic(keyword: str, bg: BackgroundTasks, size: Optional[PositiveInt] = Query(10)):
    await utils.validate_project(keyword)
    instagram_data = await fetch_instagram_data(keyword, size)
    result_data = await split_data(instagram_data, bg)

    totals = {"likesCount": 0, "sharesCount": 0, "viewsCount": 0, "commentsCount": 0}

    for x in result_data:
        totals["likesCount"] += x.get("likesCount", 0)
        totals["sharesCount"] += x.get("sharesCount", 0)
        totals["viewsCount"] += x.get("viewsCount", 0)
        totals["commentsCount"] += x.get("commentsCount", 0)

    return schemas.CollectStatistic(**totals)
