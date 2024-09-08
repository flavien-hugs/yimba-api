from typing import Optional

from apify_client import ApifyClient
from newsapi import NewsApiClient
from pydantic import PositiveInt

from src.services.config.apify import settings


class SocialMediaScraper:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(SocialMediaScraper, cls).__new__(cls)
            cls.__instance._initialize()
        return cls.__instance

    def _initialize(self):
        self.client = ApifyClient(token=settings.APIFY_TOKEN)
        self.newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        self.actors = {
            "tiktok": self.client.actor(settings.APIFY_TIKTOK_ACTOR),
            "google": self.client.actor(settings.APIFY_GOOGLE_ACTOR),
            "twitter": self.client.actor(settings.APIFY_TWITTER_ACTOR),
            "facebook": self.client.actor(settings.APIFY_FACEBOOK_ACTOR),
            "youtube": self.client.actor(settings.APIFY_YOUTUBE_ACTOR),
            "instagram": self.client.actor(settings.APIFY_INSTAGRAM_ACTOR),
        }

    async def _run_actor(self, actor_name: str, run_input: dict):
        result = self.actors[actor_name].call(run_input=run_input)
        if result["status"] != "SUCCEEDED":
            raise RuntimeError(f"The {actor_name} scraper run has failed")
        return self.client.dataset(result["defaultDatasetId"]).list_items().items

    async def scrape_facebook(self, keyword: str, results_limit: Optional[PositiveInt] = 20):
        run_input = {"keywordList": [keyword], "resultsLimit": results_limit}
        return await self._run_actor(actor_name="facebook", run_input=run_input)

    async def scrape_tiktok(self, keyword: str, results_limit: Optional[PositiveInt] = 20):
        run_input = {
            "enableCheerioBoost": True,
            "hashtags": [keyword],
            "resultsPerPage": results_limit,
            "shouldDownloadVideos": True,
            "shouldDownloadCovers": False,
            "shouldDownloadSlideshowImages": False,
            "disableEnrichAuthorStats": True,
            "disableCheerioBoost": False,
        }
        return await self._run_actor(actor_name="tiktok", run_input=run_input)

    async def scrape_twitter(self, keyword: str, tweets_desired: Optional[PositiveInt] = 20):
        run_input = {
            "handles": [keyword],
            "tweetsDesired": tweets_desired,
            "addUserInfo": True,
            "startUrls": [],
            "proxyConfig": {"useApifyProxy": True},
        }
        return await self._run_actor("twitter", run_input)

    async def scrape_instagram(self, keyword: str, results_limit: Optional[PositiveInt] = 20):
        run_input = {
            "search": keyword,
            "resultsType": "posts",
            "resultsLimit": results_limit,
            "searchType": "hashtag",
            "searchLimit": 20,
        }
        return await self._run_actor("instagram", run_input)

    async def scrape_youtube(self, keyword: str, max_results: Optional[PositiveInt] = 20):
        run_input = {
            "searchKeywords": keyword,
            "maxResults": max_results,
            "sortingOrder": "views",
            "sortChannelShortsBy": "POPULAR",
            "maxResultsShorts": 0,
            "maxResultStreams": 0,
        }
        return await self._run_actor("youtube", run_input)

    async def scrape_google(self, keyword: str, results_limit: Optional[PositiveInt] = 20):
        run_input = {
            "queries": keyword,
            "maxPagesPerQuery": 20,
            "resultsPerPage": results_limit,
            "mobileResults": True,
            "customDataFunction": """async ({ input, $, request, response, html }) => {
                return {
                    pageTitle: $('title').text(),
                };
            };""",
        }
        return await self._run_actor("google", run_input)

    async def scrape_newsapi(self, keyword: str, results_limit: Optional[PositiveInt] = 5):
        result = self.newsapi.get_everything(q=keyword, sort_by="relevancy", page=results_limit)
        if result.get("status") != "ok":
            raise RuntimeError("The NewsAPI scraper run has failed")
        return result.get("articles")


scraper = SocialMediaScraper()
