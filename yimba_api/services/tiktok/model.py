from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Tiktok(BaseModel):
    data: Dict[str, Any] = None
    analyse: Dict[str, Any] = None


class TiktokStatistic(BaseModel):
    total_likes_count: int = 0
    total_shares_count: int = 0
    total_views_count: int = 0
    total_comments_count: int = 0
    total_posts_count: int = 0


class TiktokInDB(BaseMongoModel, Tiktok):
    ...
