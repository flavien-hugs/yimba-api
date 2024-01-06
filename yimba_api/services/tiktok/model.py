from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Tiktok(BaseModel):
    data: list = None


class TiktokInDB(BaseMongoModel, Tiktok):
    ...
