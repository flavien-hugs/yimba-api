import io
import base64
from yimba_api.services import facebook, tiktok, instagram, youtube

from slugify import slugify
from wordcloud import WordCloud
import matplotlib.pyplot as plt


async def collection_keyword(keyword: str, model, storage, search) -> str:
    text = ""
    search_terms = map(slugify, keyword.split())
    items = model.find(
        storage,
        {f"data.{search}": {"$regex": term, "$options": "i"} for term in search_terms},
    )
    async for t in items:
        text += t.data.get(f"{search}", "") or ""
    return text


async def collect_keyword(keyword: str) -> str:
    text = ""

    # Récupération des données TikTok
    tiktok_data = await collection_keyword(
        keyword, tiktok.model.TiktokInDB, tiktok.api.router.storage, "text"
    )
    text += tiktok_data

    # Récupération des données Instagram
    instagram_data = await collection_keyword(
        keyword, instagram.model.InstagramInDB, instagram.api.router.storage, "caption"
    )
    text += instagram_data

    # Récupération des données Facebook
    facebook_data = await collection_keyword(
        keyword, facebook.model.FacebookInDB, facebook.api.router.storage, "text"
    )
    text += facebook_data

    # Récupération des données Youtube
    youtube_data = await collection_keyword(
        keyword, youtube.model.YoutubeInDB, youtube.api.router.storage, "text"
    )
    text += youtube_data

    return text


async def get_fb_analyse(keyword: str):
    search_filter = {
        "$or": [
            {"data.hashtag": {"$regex": keyword, "$options": "i"}},
            {"data.text": {"$regex": keyword, "$options": "i"}},
        ]
    }
    facebook_data = facebook.model.FacebookInDB.find(
        facebook.api.router.storage, search_filter
    )

    totals = {
        "fb_total_likes_count": 0,
        "fb_total_shares_count": 0,
        "fb_total_views_count": 0,
        "fb_total_comments_count": 0,
    }

    async for x in facebook_data:
        totals["fb_total_likes_count"] += x.data.get("likesCount", 0)
        totals["fb_total_shares_count"] += x.data.get("sharesCount", 0)
        totals["fb_total_views_count"] += x.data.get("viewsCount", 0)
        totals["fb_total_comments_count"] += x.data.get("commentsCount", 0)

    return totals


async def get_titktok_analyse(keyword: str):
    search_filter = {
        "$or": [
            {"data.searchHashtag.name": {"$regex": keyword, "$options": "i"}},
            {"data.hashtags": {"$regex": keyword, "$options": "i"}},
            {"data.text": {"$regex": keyword, "$options": "i"}},
        ]
    }
    tiktok_data = tiktok.model.TiktokInDB.find(tiktok.api.router.storage, search_filter)

    totals = {
        "tk_total_likes_count": 0,
        "tk_total_shares_count": 0,
        "tk_total_views_count": 0,
        "tk_total_comments_count": 0,
    }

    async for x in tiktok_data:
        totals["tk_total_likes_count"] += x.data.get("diggCount", 0)
        totals["tk_total_shares_count"] += x.data.get("shareCount", 0)
        totals["tk_total_views_count"] += x.data.get("playCount", 0)
        totals["tk_total_comments_count"] += x.data.get("commentCount", 0)

    return totals


async def get_yt_analyse(keyword: str):
    search_filter = {
        "$or": [
            {"data.title": {"$regex": keyword, "$options": "i"}},
            {"data.text": {"$regex": keyword, "$options": "i"}},
        ]
    }
    youtube_data = youtube.model.YoutubeInDB.find(
        youtube.api.router.storage, search_filter
    )

    totals = {
        "yt_total_likes_count": 0,
        "yt_total_shares_count": 0,
        "yt_total_views_count": 0,
        "yt_total_comments_count": 0,
    }

    async for x in youtube_data:
        totals["yt_total_likes_count"] += x.data.get("likes", 0)
        totals["yt_total_shares_count"] += x.data.get("shareCount", 0)
        totals["yt_total_views_count"] += x.data.get("viewCount", 0)
        totals["yt_total_comments_count"] += x.data.get("commentsCount", 0)

    return totals


async def get_insta_analyse(keyword: str):
    search_filter = {
        "$or": [
            {"data.hashtags": {"$regex": keyword, "$options": "i"}},
            {"data.alt": {"$regex": keyword, "$options": "i"}},
        ]
    }
    insta_data = instagram.model.InstagramInDB.find(
        instagram.api.router.storage, search_filter
    )

    totals = {"in_total_likes_count": 0, "in_total_comments_count": 0}

    async for x in insta_data:
        totals["in_total_likes_count"] += x.data.get("likesCount", 0)
        totals["in_total_comments_count"] += x.data.get("commentsCount", 0)

    return totals


async def fb_graphic(keyword: str):
    fb_analyse = await get_fb_analyse(keyword)
    tk_analyse = await get_titktok_analyse(keyword)
    in_analyse = await get_insta_analyse(keyword)
    yt_analyse = await get_yt_analyse(keyword)

    labels = ["Likes", "Partages", "Vues", "Commentaires"]

    likes = (
        in_analyse.get("in_total_likes_count")
        + yt_analyse.get("yt_total_likes_count")
        + fb_analyse.get("fb_total_likes_count")
        + tk_analyse.get("tk_total_likes_count")
    )

    shares = (
        fb_analyse.get("fb_total_shares_count")
        + tk_analyse.get("tk_total_shares_count")
        + yt_analyse.get("yt_total_shares_count")
    )

    views = (
        fb_analyse.get("fb_total_views_count")
        + tk_analyse.get("tk_total_views_count")
        + yt_analyse.get("yt_total_views_count")
    )

    comments = (
        in_analyse.get("in_total_comments_count")
        + fb_analyse.get("fb_total_comments_count")
        + tk_analyse.get("tk_total_comments_count")
        + yt_analyse.get("yt_total_comments_count")
    )

    sizes = [likes, shares, views, comments]

    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))
    ax.pie(
        sizes,
        wedgeprops=dict(width=0.5, edgecolor="w"),
        startangle=30,
        explode=(0.1, 0, 0, 0.1),
        labels=labels,
        autopct="%1.1f%%",
    )

    # Enregistrer la figure dans un flux d'octets
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    # Convertir les octets en base64
    img_base64 = base64.b64encode(img.read()).decode("utf-8")
    img_str = "data:image/png;base64,{0}".format(img_base64)

    return {"fb_graphic_img": img_str}


async def process_text_facebook(keyword: str):

    text = await collect_keyword(keyword)
    wordcloud = WordCloud(
        collocations=False, background_color="white", max_words=200, min_word_length=4
    )
    process_text = wordcloud.process_text(text)
    keywords = list(process_text.keys())
    return {"fb_keywords": keywords}


async def generate_cloud_tags_facebook(keyword: str) -> str:
    wordcloud = WordCloud(
        collocations=False, background_color="white", max_words=300, min_word_length=4
    )
    text = await collect_keyword(keyword)
    generate_text = wordcloud.generate_from_text(text)
    image_bytes = io.BytesIO()
    generate_text.to_image().save(image_bytes, format="PNG")

    cloudtags_image = "data:image/png;base64,{0}".format(
        base64.b64encode(image_bytes.getvalue()).decode("utf-8")
    )

    return {"fb_cloudtag_img": cloudtags_image}
