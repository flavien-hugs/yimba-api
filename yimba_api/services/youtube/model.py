from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Youtube(BaseModel):
    data: Dict[str, Any] = None
    analyse: Dict[str, Any] = None


class YoutubeStatistic(BaseModel):
    total_likes_count: int = 0
    total_shares_count: int = 0
    total_views_count: int = 0
    total_comments_count: int = 0
    total_posts_count: int = 0


class YoutubeInDB(BaseMongoModel, Youtube):
    ...
