from typing import Dict, Any
from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Google(BaseModel):
    data: Dict[str, Any] = None
    analyse: Dict[str, Any] = None


class GoogleInDB(BaseMongoModel, Google):
    ...
