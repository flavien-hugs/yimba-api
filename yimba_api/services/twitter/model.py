from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Twitter(BaseModel):
    data: Dict[str, Any] = None


class TwitterInDB(BaseMongoModel, Twitter):
    ...
