from apify_client import ApifyClient
from yimba_api.config.apify import settings

client = ApifyClient(settings.apify_token)
run = client.actor(settings.apify_actor_id)


async def scrapping_facebook_data(keyword: str):
    result = run.call(run_input={"keywordList": [keyword], "resultsLimit": 5})
    dataset = client.dataset(result["defaultDatasetId"]).list_items().items
    return dataset
