import logging
from typing import Optional

from fastapi import Depends, Query, status
from fastapi_pagination.ext.beanie import paginate
from pymongo import ASCENDING, DESCENDING

from src.common.helpers.exceptions import CustomHTTException
from src.common.helpers.permissions import CheckAccessAllow
from src.services import models, router_factory
from src.shared import crud
from src.shared.error_codes import YimbaApifyErrorCode
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL
from src.shared.utils import SortEnum

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/analyses",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=crud.customize_page(models.Analyse),
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["analyse:can-display-display"]))],
    summary="Get all analyse sentiments by posts",
    status_code=status.HTTP_200_OK,
)
async def get_post_sentiment(
    post_id: Optional[str] = Query(None, description="Search by post ID"),
    sort: Optional[SortEnum] = Query(
        SortEnum.DESC,
        description="Order by creation date: 'asc' or 'desc",
    ),
):
    query = {}
    if post_id:
        query["post_id"] = post_id

    sorted = DESCENDING if sort == SortEnum.DESC else ASCENDING

    analyses = models.Analyse.find(query, sort=[("created_at", sorted)])
    return paginate(analyses)


@router.get(
    "/{id}",
    response_model=models.Analyse,
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["analyse:can-display-display"]))],
    summary="Get single analyse post sentiment",
    status_code=status.HTTP_200_OK,
)
async def get_analyse(id: str):
    if (document := await models.Analyse.find_one({"post_id": id})) is None:
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.DOCUMENT_NOT_FOUND,
            message_error="Document not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return document
