from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Facebook(BaseModel):
    data: list = None


class FacebookInDB(BaseMongoModel, Facebook):
    ...
