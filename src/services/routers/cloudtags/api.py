import logging

from fastapi import HTTPException, Depends, status
from fastapi.responses import JSONResponse
from src.common.helpers.permissions import CheckAccessAllow
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

from src.services import router_factory
from src.shared.utils import collect_keyword

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/cloudtags",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/{keyword}",
    dependencies=[
        Depends(
            CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["cloudtags:can-generete-cloudtags"]))],
    status_code=status.HTTP_200_OK,
    summary="Generate cloud tags",
)
async def generate_cloudtags(keyword: str):
    try:
        text = await collect_keyword(keyword)
        result = JSONResponse(status_code=status.HTTP_200_OK, content={"tags": text})
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return result
