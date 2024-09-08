import logging

from fastapi import Depends, status

from src.common.helpers.permissions import CheckAccessAllow
from src.services import router_factory
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/cloudtags",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/{keyword}",
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["cloudtags:can-generete-cloudtags"]))
    ],
    status_code=status.HTTP_200_OK,
    summary="Generate cloud tags",
)
async def generate_cloudtags(keyword: str):
    pass
