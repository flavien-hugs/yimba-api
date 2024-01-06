from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Twitter(BaseModel):
    data: list = None


class TwitterInDB(BaseMongoModel, Twitter):
    ...
