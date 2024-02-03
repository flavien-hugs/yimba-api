import logging
from io import BytesIO
from typing import Optional

from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import HTTPException, Query, Security, status

from slugify import slugify
from wordcloud import WordCloud
from fastapi_pagination import paginate

from yimba_api.services.instagram import model
from yimba_api.services import router_factory
from yimba_api.shared import scrapper, crud, service
from yimba_api.shared.authentication import AuthTokenBearer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

router = router_factory(
    prefix="/api/instagram",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/",
    response_model=crud.CustomPage[model.InstagramInDB],
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    summary="Search Instagram by hashtag",
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
        items = model.InstagramInDB.find(router.storage, {})
        return paginate([item async for item in items])

    search_terms = map(slugify, query.split())
    search_filter = {
        "$or": [
            {"data.hashtags": {"$regex": query, "$options": "i"}}
            for term in search_terms
        ]
        + [{"data.alt": {"$regex": query, "$options": "i"}} for term in search_terms]
    }
    items = model.InstagramInDB.find(router.storage, search_filter)
    return paginate([item async for item in items])


@router.get(
    "/{keyword}", summary="Get Instagram hashtag", status_code=status.HTTP_200_OK
)
async def get_instagram_hashtag(
    keyword: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "client"])),
):
    """
    Grattez et téléchargez des posts, profils, lieux, hashtags, photos et commentaires
    Instagram. Obtenez des données d'Instagram à l'aide d'un hashtag Instagram
    ou de requêtes de recherche.
    """
    try:
        instagram_data = await scrapper.scrapping_instagram_data(keyword)
        topsposts = instagram_data[0].get("topPosts", "")
    except Exception as err:
        logger.error(f"An error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err

    for data in topsposts:
        apc = analyzer.polarity_scores(data.get("caption"))
        result = await model.InstagramInDB(data=data, analyse=apc).save(router.storage)
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
    summary="Remove Instagram information",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_instagram_information(id: str):
    return await crud.delete(router.storage, model.InstagramInDB, id)


@router.get(
    "/{keyword}/statistics",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
    response_model=model.InstagramStatistic,
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
        instagram_data = model.InstagramInDB.find(router.storage, search_filter)
        instagram_data_count = await model.InstagramInDB.count(
            router.storage, search_filter
        )

        totals = {
            "total_likes_count": 0,
            "total_comments_count": 0,
            "total_posts_count": instagram_data_count,
        }

        async for x in instagram_data:
            totals["total_likes_count"] += x.data.get("likesCount", 0)
            totals["total_comments_count"] += x.data.get("commentsCount", 0)

        result = model.InstagramStatistic(**totals)

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
                {"data.hashtags": {"$regex": keyword, "$options": "i"}},
                {"data.alt": {"$regex": keyword, "$options": "i"}},
            ]
        }
        items = model.InstagramInDB.find(router.storage, search_filter)
        text = ""
        async for t in items:
            text += t.data.get("hashtags", "") + " "

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
