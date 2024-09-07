from typing import Optional
from pydantic import BaseModel, PositiveInt
from typing import Dict, Any


class CollectData(BaseModel):
    data: Dict[str, Any] = None
    analyse: Dict[str, Any] = None


class CollectStatistic(BaseModel):
    total_likes_count: Optional[PositiveInt] = 0
    total_shares_count: Optional[PositiveInt] = 0
    total_views_count: Optional[PositiveInt] = 0
    total_comments_count: Optional[PositiveInt] = 0
    total_posts_count: Optional[PositiveInt] = 0


class CreateAnalyse(BaseModel):
    post_id: str
    neutre: float
    negatif: float
    positif: float
    compound: float


class CreateProject(BaseModel):
    name: str
    description: Optional[str] = None
