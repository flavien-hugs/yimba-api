from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Google(BaseModel):
    data: list = None


class GoogleInDB(BaseMongoModel, Google):
    ...
