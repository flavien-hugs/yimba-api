from apify_client import ApifyClient

client = ApifyClient(token="apify_api_zp9DObAiihR4hVAK1Y1ouGlmKJY3u72Ki7e5")


run_input = {
    "searchKeywords": "can2023",
    "maxResults": 10,
    "maxResultsShorts": 0,
    "maxResultStreams": 0,
}

run = client.actor("streamers/youtube-scraper").call(run_input=run_input)

dataset = client.dataset(run["defaultDatasetId"]).list_items().items
print("dataset --> ", dataset)
