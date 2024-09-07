from newsapi import NewsApiClient
from apify_client import ApifyClient

from src.services.config.apify import settings

client = ApifyClient(token=settings.APIFY_TOKEN)
newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
tiktok_actor_run = client.actor(settings.APIFY_TIKTOK_ACTOR)
google_actor_run = client.actor(settings.APIFY_GOOGLE_ACTOR)
twitter_actor_run = client.actor(settings.APIFY_TWITTER_ACTOR)
facebook_actor_run = client.actor(settings.APIFY_FACEBOOK_ACTOR)
youtube_actor_run = client.actor(settings.APIFY_YOUTUBE_ACTOR)
instagram_actor_run = client.actor(settings.APIFY_INSTAGRAM_ACTOR)


async def scrapping_facebook_data(keyword: str):
    result = facebook_actor_run.call(run_input={"keywordList": [keyword], "resultsLimit": 20})
    if result["status"] != "SUCCEEDED":
        raise RuntimeError("The facebook scraper run has failed")
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset


async def scrapping_tiktok_data(keyword: str):
    run_input = {
        "enableCheerioBoost": True,
        "hashtags": [keyword],
        "resultsPerPage": 20,
        "shouldDownloadVideos": True,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "disableEnrichAuthorStats": True,
        "disableCheerioBoost": False,
    }
    result = tiktok_actor_run.call(run_input=run_input)
    if result["status"] != "SUCCEEDED":
        raise RuntimeError("The CollecteTiktokData scraper run has failed")
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset


async def scrapping_twitter_data(keyword: str):
    run_input = {
        "handles": [keyword],
        "tweetsDesired": 10,
        "addUserInfo": True,
        "startUrls": [],
        "proxyConfig": {"useApifyProxy": True},
    }
    result = twitter_actor_run.call(run_input=run_input)
    if result["status"] != "SUCCEEDED":
        raise RuntimeError("The CollectTwitterData scraper run has failed")
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset


async def scrapping_instagram_data(keyword: str):
    run_input = {
        "search": keyword,
        "resultsType": "posts",
        "resultsLimit": 20,
        "searchType": "hashtag",
        "searchLimit": 20,
    }
    result = instagram_actor_run.call(run_input=run_input)
    if result["status"] != "SUCCEEDED":
        raise RuntimeError("The Instragram scraper run has failed")
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset


async def scrapping_youtube_data(keyword: str):
    run_input = {
        "searchKeywords": keyword,
        "maxResults": 10,
        "sortingOrder": "views",
        "sortChannelShortsBy": "POPULAR",
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
    }
    result = youtube_actor_run.call(run_input=run_input)
    if result["status"] != "SUCCEEDED":
        raise RuntimeError("The CollectYoutubeData scraper run has failed")
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset


async def scrapping_google_data(keyword: str):
    run_input = {
        "queries": keyword,
        "maxPagesPerQuery": 20,
        "resultsPerPage": 20,
        "mobileResults": True,
        "customDataFunction": """async ({ input, $, request, response, html }) => {
            return {
                pageTitle: $('title').text(),
            };
        };""",
    }
    result = google_actor_run.call(run_input=run_input)
    if result["status"] != "SUCCEEDED":
        raise RuntimeError("The ColllectGoogleData scraper run has failed")
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset


async def scrapping_newsapi(keyword: str):
    result = newsapi.get_everything(q=keyword, sort_by="relevancy", page=5)
    if result.get("status") != "ok":
        raise RuntimeError("The NewsAPI scraper run has failed")
    return result.get("articles")
