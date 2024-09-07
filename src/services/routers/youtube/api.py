import logging
from io import BytesIO
from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_pagination import paginate
from slugify import slugify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud

from src.common.helpers.permissions import CheckAccessAllow
from src.services import models, router_factory, schemas
from src.shared import crud, scrapper
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

router = router_factory(
    prefix="/youtube",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=crud.customize_page(models.Youtube),
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["youtube:can-display-youtube-data"]))],
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
        items = src.services.models.models.Youtube.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [{"data.title": {"$regex": term, "$options": "i"}} for term in search_terms]
        + [{"data.text": {"$regex": term, "$options": "i"}} for term in search_terms]
    }
    items = src.services.models.models.Youtube.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Depends(
        CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["youtube:can-extract-data-from-youtube-posts"]))],
    summary="Get youtube hashtag",
    status_code=status.HTTP_200_OK
)
async def get_youtube_hashtag(keyword: str):
    try:
        scraping = await scrapper.scrapping_youtube_data(keyword)
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err

    for data in scraping:
        apc = analyzer.polarity_scores(data.get("text"))
        result = await models.Youtube(data=data, analyse=apc).save(router.storage)

        """
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
        """

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Scrapping successful!"})


@router.delete(
    "/{id}",
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["youtube:can-delete-data-from-youtube"]))],
    summary="Remove youtube information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_youtube_information(id: str):
    return await crud.delete(router.storage, models.Youtube, id)


@router.get(
    "/{keyword}/statistics",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL,
                                           permissions=["youtube:can-read-scrapper-youtube-data-statistics"]))],
    response_model=schemas.CollectStatistic,
    summary="Get CollectYoutubeData scrapper data statictics",
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
        youtube_data = models.Youtube.find(router.storage, search_filter)
        youtube_data_count = await models.Youtube.count(router.storage, search_filter)

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

        result = schemas.CollectStatistic(**totals)

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return result


@router.get(
    "/{keyword}/cloudtags",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL,
                                           permissions=["youtube:can-generate-word-cloud-youtube-keywords"]))],
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
        items = models.Youtube.find(router.storage, search_filter)
        text = ""
        async for t in items:
            text += t.data.get("text", "") + " "

        word_cloud = WordCloud(collocations=False, background_color="white").generate_from_text(text)
        image = word_cloud.to_image()
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")

        body = BytesIO(image_bytes.getvalue())

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return StreamingResponse(body, media_type="image/png")
