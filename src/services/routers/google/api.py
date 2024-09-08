import logging
from itertools import chain
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, Depends, HTTPException, Query, status
from fastapi_pagination import paginate
from pydantic import PositiveInt
from src.common.helpers.exceptions import CustomHTTException
from src.common.helpers.permissions import CheckAccessAllow
from src.services import router_factory
from src.shared import crud, utils
from src.shared.auth_handler import CheckUserInfoHandler
from src.shared.error_codes import YimbaApifyErrorCode
from src.shared.scrapper import scraper
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/google",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


async def fetch_google_data(keyword: str, size: Optional[PositiveInt] = 10):
    try:
        result = await scraper.scrape_google(keyword=keyword, results_limit=size)
    except HTTPException as exc:
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.BAD_REQUEST, message_error=str(exc), status_code=status.HTTP_400_BAD_REQUEST
        ) from exc

    return result


async def split_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result_data = []

    for item in data:
        related_queries = item.get("relatedQueries", [])
        organic_results = item.get("organicResults", [])

        posts = list(chain(related_queries, organic_results))
        result_data.extend(posts)

    return result_data


@router.get(
    "",
    response_model=crud.customize_page(dict),
    dependencies=[
        Depends(
            CheckAccessAllow(
                url=CHECK_ACCESS_ALLOW_URL, permissions=["google:can-extract-data-from-google-search-engine"]
            )
        )
    ],
    summary="Search Colllect Google Data by hashtag",
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

    result = await fetch_google_data(keyword, size)
    data = await split_data(data=result)

    return paginate(data)
