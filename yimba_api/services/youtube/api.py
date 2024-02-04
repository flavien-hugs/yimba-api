import logging
from io import BytesIO
from typing import Optional

from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import HTTPException, Query, Security, status

from slugify import slugify
from wordcloud import WordCloud
from fastapi_pagination import paginate

from yimba_api.services import router_factory
from yimba_api.services.youtube import model
from yimba_api.shared import crud, scrapper, service
from yimba_api.shared.authentication import AuthTokenBearer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

router = router_factory(
    prefix="/api/youtube",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/",
    response_model=crud.CustomPage[model.YoutubeInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Search youtube by hashtag",
    status_code=status.HTTP_200_OK,
)
async def search(
    query: Optional[str] = Query(
        None,
        alias="search",
        description="Search by items: hashtag, text",
    )
):
    if query is None:
        items = model.YoutubeInDB.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [
            {"data.title": {"$regex": term, "$options": "i"}} for term in search_terms
        ]
        + [{"data.text": {"$regex": term, "$options": "i"}} for term in search_terms]
    }
    items = model.YoutubeInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get("/{keyword}", summary="Get youtube hashtag", status_code=status.HTTP_200_OK)
async def get_youtube_hashtag(
    keyword: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    try:
        scraping = await scrapper.scrapping_youtube_data(keyword)
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err

    for data in scraping:
        apc = analyzer.polarity_scores(data.get("text"))
        result = await model.YoutubeInDB(data=data, analyse=apc).save(router.storage)
        await service.analyse_post_text(
            {
                "post_id": result.inserted_id,
                "neutre": apc.get("neu"),
                "negatif": apc.get("neg"),
                "positif": apc.get("pos"),
                "compound": apc.get("compound"),
            },
            current_user,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Scrapping successful!"}
    )


@router.delete(
    "/{id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Remove youtube information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_youtube_information(id: str):
    return await crud.delete(router.storage, model.YoutubeInDB, id)


@router.get(
    "/{keyword}/statistics",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    response_model=model.YoutubeStatistic,
    summary="Get Youtube scrapper data statictics",
    status_code=status.HTTP_200_OK,
)
async def statistic(keyword: str):
    try:
        search_filter = {
            "$or": [
                {"data.title": {"$regex": keyword, "$options": "i"}},
                {"data.text": {"$regex": keyword, "$options": "i"}},
            ]
        }
        youtube_data = model.YoutubeInDB.find(router.storage, search_filter)
        youtube_data_count = await model.YoutubeInDB.count(
            router.storage, search_filter
        )

        totals = {
            "total_likes_count": 0,
            "total_shares_count": 0,
            "total_views_count": 0,
            "total_comments_count": 0,
            "total_posts_count": youtube_data_count,
        }

        async for x in youtube_data:
            totals["total_likes_count"] += x.data.get("likes", 0)
            totals["total_shares_count"] += x.data.get("shareCount", 0)
            totals["total_views_count"] += x.data.get("viewCount", 0)
            totals["total_comments_count"] += x.data.get("commentsCount", 0)

        result = model.YoutubeStatistic(**totals)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc

    return result


@router.get(
    "/{keyword}/cloudtags",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Generate a word cloud",
    status_code=status.HTTP_200_OK,
)
async def generate_word_cloud(keyword: str):
    try:
        search_filter = {
            "$or": [
                {"data.title": {"$regex": keyword, "$options": "i"}},
                {"data.text": {"$regex": keyword, "$options": "i"}},
            ]
        }
        items = model.YoutubeInDB.find(router.storage, search_filter)
        text = ""
        async for t in items:
            text += t.data.get("text", "") + " "

        word_cloud = WordCloud(
            collocations=False, background_color="white"
        ).generate_from_text(text)
        image = word_cloud.to_image()
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")

        body = BytesIO(image_bytes.getvalue())

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc

    return StreamingResponse(body, media_type="image/png")
