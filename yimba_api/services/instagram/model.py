from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Instagram(BaseModel):
    data: Dict[str, Any] = None
    analyse: Dict[str, Any] = None


class InstagramStatistic(BaseModel):
    total_likes_count: int = 0
    total_comments_count: int = 0
    total_posts_count: int = 0


class InstagramInDB(BaseMongoModel, Instagram):
    ...
