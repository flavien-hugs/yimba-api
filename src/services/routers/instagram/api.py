import logging
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_pagination import paginate
from slugify import slugify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud

from src.common.helpers.permissions import CheckAccessAllow
from src.services import models, schemas
from src.shared import crud, scrapper
from src.shared.url_patterns import CHECK_ACCESS_ALLOW_URL

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

router = APIRouter(
    prefix="/instagram",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=crud.customize_page(models.Instagram),
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["instagram:can-display-data-from-instagram"]))],
    summary="Search instagram data by hashtag",
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
        items = models.Instagram.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [{"data.hashtags": {"$regex": query, "$options": "i"}} for term in search_terms]
        + [{"data.alt": {"$regex": query, "$options": "i"}} for term in search_terms]
    }
    items = models.Instagram.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["instagram:can-extract-data-from-instagram"]))],
    summary="Get CollecteInstagramData hashtag",
    status_code=status.HTTP_200_OK,
)
async def get_instagram_hashtag(keyword: str):
    """
    Grattez et téléchargez des posts, profils, lieux, hashtags, photos et commentaires
    Instagram. Obtenez des données d'CollecteInstagramData à l'aide d'un hashtag CollecteInstagramData
    ou de requêtes de recherche.
    """
    try:
        instagram_data = await scrapper.scrapping_instagram_data(keyword)
        topsposts = instagram_data[0].get("topPosts", "")
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err

    for data in topsposts:
        apc = analyzer.polarity_scores(data.get("caption"))
        result = await models.Instagram(data=data, analyse=apc).save(router.storage)
        # await service.analyse_post_text(
        #     {
        #         "post_id": result.inserted_id,
        #         "neutre": apc.get("neu"),
        #         "negatif": apc.get("neg"),
        #         "positif": apc.get("pos"),
        #         "compound": apc.get("compound"),
        #     },
        #     current_user,
        # )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Scrapping successful!"})


@router.delete(
    "/{id}",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["instagram:can-delete-data-from-instagram"]))],
    summary="Remove Instagram information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_instagram_information(id: str):
    return await crud.delete(router.storage, models.Instagram, id)


@router.get(
    "/{keyword}/statistics",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["instagram:can-read-scrapper-instagram-data-statistics"]))],
    response_model=schemas.CollectStatistic,
    summary="Get instagram scrapper data statictics",
    status_code=status.HTTP_200_OK,
)
async def statistic(keyword: str):
    try:
        search_filter = {
            "$or": [
                {"data.hashtags": {"$regex": keyword, "$options": "i"}},
                {"data.alt": {"$regex": keyword, "$options": "i"}},
            ]
        }
        instagram_data = models.Instagram.find(router.storage, search_filter)
        instagram_data_count = await models.Instagram.count(router.storage, search_filter)

        totals = {
            "total_likes_count": 0,
            "total_comments_count": 0,
            "total_posts_count": instagram_data_count,
        }

        async for x in instagram_data:
            totals["total_likes_count"] += x.data.get("likesCount", 0)
            totals["total_comments_count"] += x.data.get("commentsCount", 0)

        result = schemas.CollectStatistic(**totals)

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return result


@router.get(
    "/{keyword}/cloudtags",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["instagram:can-read-cloudtags"]))],
    summary="Generate a word cloud",
    status_code=status.HTTP_200_OK,
)
async def generate_word_cloud(keyword: str):
    try:
        search_filter = {
            "$or": [
                {"data.hashtags": {"$regex": keyword, "$options": "i"}},
                {"data.alt": {"$regex": keyword, "$options": "i"}},
            ]
        }
        items = models.Instagram.find(router.storage, search_filter)
        text = ""
        async for t in items:
            text += t.data.get("hashtags", "") + " "

        word_cloud = WordCloud(collocations=False, background_color="white").generate_from_text(text)
        image = word_cloud.to_image()
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")

        body = BytesIO(image_bytes.getvalue())

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return StreamingResponse(body, media_type="image/png")
