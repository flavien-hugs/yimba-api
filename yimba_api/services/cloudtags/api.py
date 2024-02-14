import logging
import base64
from io import BytesIO
from fastapi import Security, HTTPException, status
from fastapi.responses import StreamingResponse

from slugify import slugify
from wordcloud import WordCloud
from yimba_api.services import router_factory
from yimba_api.shared.authentication import AuthTokenBearer
from yimba_api.services import facebook, tiktok, instagram, youtube

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
async def generate_cloudtags(
    keyword: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    try:
        text = ""

        search_terms = map(slugify, keyword.split())

        # Récupération des données TikTok
        tiktok_data = tiktok.model.TiktokInDB.find(
            router.storage,
            {"data.text": {"$regex": term, "$options": "i"} for term in search_terms}
        )
        async for t in tiktok_data:
            text += t.data.get("text", "") or ""

        # Récupération des données Instagram
        instagram_data = instagram.model.InstagramInDB.find(
            router.storage,
            {"data.caption": {"$regex": term, "$options": "i"} for term in search_terms}
        )
        async for t in instagram_data:
            text += (t.data.get("caption", "") or "") + (t.data.get("alt", "") or "")

        # Récupération des données Facebook
        facebook_data = facebook.model.FacebookInDB.find(
            router.storage,
            {"data.text": {"$regex": term, "$options": "i"} for term in search_terms},
        )
        async for t in facebook_data:
            text += t.data.get("text", "") or ""

        # Récupération des données Youtube
        youtube_data = youtube.model.YoutubeInDB.find(
            router.storage,
            {"data.text": {"$regex": term, "$options": "i"} for term in search_terms}
        )
        async for t in youtube_data:
            text += (t.data.get("text", "") or "") + (t.data.get("title", "") or "")

        word_cloud = WordCloud(
            collocations=False, background_color="white"
        ).generate_from_text(text)
        image_bytes = BytesIO()
        word_cloud.to_image().save(image_bytes, format="PNG")
        base64_image = base64.b64encode(image_bytes.getvalue()).decode("utf-8")

        result = f"<img src='data:image/png;base64,{base64_image}'>"

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc

    return result
