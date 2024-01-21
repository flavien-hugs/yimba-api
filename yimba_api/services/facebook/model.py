from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Facebook(BaseModel):
    data: Dict[str, Any] = None
    analyse: Dict[str, Any] = None


class FacebookInDB(BaseMongoModel, Facebook):
    ...
