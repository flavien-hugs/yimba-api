from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Youtube(BaseModel):
    data: Dict[str, Any] = None


class YoutubeInDB(BaseMongoModel, Youtube):
    ...
