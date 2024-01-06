from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Instagram(BaseModel):
    data: list = None


class InstagramInDB(BaseMongoModel, Instagram):
    ...
