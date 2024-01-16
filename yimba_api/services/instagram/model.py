from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Instagram(BaseModel):
    data: Dict[str, Any] = None


class InstagramInDB(BaseMongoModel, Instagram):
    ...
