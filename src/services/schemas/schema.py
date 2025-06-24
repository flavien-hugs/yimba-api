from typing import Optional
from pydantic import BaseModel
from typing import Dict, Any


class CollectData(BaseModel):
    data: Dict[str, Any] = None
    analyse: Dict[str, Any] = None


class CollectStatistic(BaseModel):
    likesCount: Optional[int] = 0
    sharesCount: Optional[int] = 0
    viewsCount: Optional[int] = 0
    commentsCount: Optional[int] = 0


class FacebookResponse(CollectStatistic):
    id: str
    postId: str
    feedbackId: str
    user: Dict[str, Any]
    text: str
    url: str
    date: str
    hashtag: str


class CreateAnalyse(BaseModel):
    post_id: str
    neutre: float
    negatif: float
    positif: float
    compound: float


class CreateProject(BaseModel):
    name: str
