from newsapi import NewsApiClient
from apify_client import ApifyClient

from yimba_api.config.apify import settings

client = ApifyClient(token=settings.apify_token)
newsapi = NewsApiClient(api_key=settings.newsapi_key)
tiktok_actor_run = client.actor(settings.apify_tiktok_actor)
google_actor_run = client.actor(settings.apify_google_actor)
twitter_actor_run = client.actor(settings.apify_twitter_actor)
facebook_actor_run = client.actor(settings.apify_facebook_actor)
youtube_actor_run = client.actor(settings.apify_youtube_actor)
instagram_actor_run = client.actor(settings.apify_instagram_actor)


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
        raise RuntimeError("The Tiktok scraper run has failed")
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
        raise RuntimeError("The Twitter scraper run has failed")
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
        raise RuntimeError("The Youtube scraper run has failed")
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
        raise RuntimeError("The Google scraper run has failed")
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset


async def scrapping_newsapi(keyword: str):
    result = newsapi.get_everything(q=keyword, sort_by="relevancy", page=5)
    if result.get("status") != "ok":
        raise RuntimeError("The NewsAPI scraper run has failed")
    return result.get("articles")
