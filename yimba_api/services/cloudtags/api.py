import logging
import base64
from io import BytesIO
from fastapi import Security, HTTPException, status
from fastapi.responses import JSONResponse

from wordcloud import WordCloud
from yimba_api.services import router_factory
from yimba_api.shared.utils import collect_keyword
from yimba_api.shared.authentication import AuthTokenBearer

logger = logging.getLogger(__name__)

router = router_factory(
    prefix="/api/cloudtags",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/{keyword}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    status_code=status.HTTP_200_OK,
    summary="Generate cloud tags",
)
async def generate_cloudtags(keyword: str):
    try:
        text = await collect_keyword(keyword)
        wordcloud = WordCloud(
            collocations=False, background_color="white"
        ).generate_from_text(text)

        result = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"wordcloud": wordcloud}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc

    return result
