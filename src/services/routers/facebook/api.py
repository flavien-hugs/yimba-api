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
    prefix="/facebook",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=crud.customize_page(models.Facebook),
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["facebook:can-display-facebook-data"]))],
    summary="Search facebook by hashtag",
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
        items = models.Facebook.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [{"data.hashtag": {"$regex": term, "$options": "i"}} for term in search_terms]
        + [{"data.text": {"$regex": term, "$options": "i"}} for term in search_terms]
        + [{"data.postId": {"$regex": term, "$options": "i"}} for term in search_terms]
    }
    items = models.Facebook.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}",
    dependencies=[Depends(
        CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["facebook:can-extract-data-from-facebook-posts"]))],
    summary="Get facebook hashtag",
    status_code=status.HTTP_200_OK,
)
async def get_facebook_hashtag(keyword: str):
    """
    Extrayez des données de centaines de posts Facebook en utilisant un ou plusieurs hashtags.
    Obtenez le texte et l'URL de la publication, l'heure de la publication, les informations
    de base sur la publication, les URL des images et des vidéos, le texte OCR, le nombre de likes,
    de commentaires et de partages, et bien plus encore.
    """
    try:
        scraping = await scrapper.scrapping_facebook_data(keyword)
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err

    for data in scraping:
        apc = analyzer.polarity_scores(data.get("text"))
        result = await models.Facebook(data=data, analyse=apc).save(router.storage)
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
    dependencies=[
        Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL, permissions=["facebook:can-delete-data-from-facebook"]))],
    summary="Remove facebook collect data information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_facebook_information(id: str):
    return await crud.delete(router.storage, models.Facebook, id)


@router.get(
    "/{keyword}/statistics",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL,
                                           permissions=["facebook:can-read-scrapper-facebook-data-statistics"]))],
    response_model=schemas.CollectStatistic,
    summary="Get facebook scrapper data statictics",
    status_code=status.HTTP_200_OK,
)
async def statistic(keyword: str):
    try:
        search_filter = {
            "$or": [
                {"data.hashtag": {"$regex": keyword, "$options": "i"}},
                {"data.text": {"$regex": keyword, "$options": "i"}},
            ]
        }
        facebook_data = models.Facebook.find(router.storage, search_filter)
        facebook_data_count = await models.Facebook.count(router.storage, search_filter)

        totals = {
            "total_likes_count": 0,
            "total_shares_count": 0,
            "total_views_count": 0,
            "total_comments_count": 0,
            "total_posts_count": facebook_data_count,
        }

        async for x in facebook_data:
            totals["total_likes_count"] += x.data.get("likesCount", 0)
            totals["total_shares_count"] += x.data.get("sharesCount", 0)
            totals["total_views_count"] += x.data.get("viewsCount", 0)
            totals["total_comments_count"] += x.data.get("commentsCount", 0)

        result = schemas.CollectStatistic(**totals)

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return result


@router.get(
    "/{keyword}/cloudtags",
    dependencies=[Depends(CheckAccessAllow(url=CHECK_ACCESS_ALLOW_URL,
                                           permissions=["facebook:can-generate-word-cloud-facebook-keywords"]))],
    summary="Generate a word cloud",
    status_code=status.HTTP_200_OK,
)
async def generate_word_cloud(keyword: str):
    try:
        items = models.Facebook.find(router.storage, {"data.text": {"$regex": keyword, "$options": "i"}})
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
