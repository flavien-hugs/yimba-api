import logging
from io import BytesIO
from fastapi import Security, HTTPException, status
from fastapi.responses import StreamingResponse

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

        # Récupération des données TikTok
        tiktok_data = tiktok.model.TiktokInDB.find(
            router.storage, {"data.text": {"$regex": keyword, "$options": "i"}}
        )
        async for t in tiktok_data:
            text += t.data.get("text", "") + " "

        # Récupération des données Instagram
        instagram_data = instagram.model.InstagramInDB.find(
            router.storage, {"data.caption": {"$regex": keyword, "$options": "i"}}
        )
        async for t in instagram_data:
            text += t.data.get("caption", "") + t.data.get("alt", "") + " "

        # Récupération des données Facebook
        facebook_data = facebook.model.FacebookInDB.find(
            router.storage, {"data.text": {"$regex": keyword, "$options": "i"}}
        )
        async for t in facebook_data:
            text += t.data.get("text", "") + " "

        # Récupération des données Youtube
        youtube_data = youtube.model.YoutubeInDB.find(
            router.storage, {"data.text": {"$regex": keyword, "$options": "i"}}
        )
        async for t in youtube_data:
            text += t.data.get("text", "") + t.data.get("title", "") + " "

        word_cloud = WordCloud(
            collocations=False, background_color="white"
        ).generate_from_text(text)
        image = word_cloud.to_image()
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")

        body = BytesIO(image_bytes.getvalue())

        result = StreamingResponse(body, media_type="image/png")

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc

    return result
