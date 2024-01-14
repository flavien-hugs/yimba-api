from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Youtube(BaseModel):
    data: list = None


class YoutubeInDB(BaseMongoModel, Youtube):
    ...
