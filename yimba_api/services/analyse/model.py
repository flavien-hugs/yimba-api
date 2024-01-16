from pydantic import BaseModel
from yimba_api import BaseMongoModel


class Analyse(BaseModel):
    post_id: str
    neutre: float
    negatif: float
    positif: float
    compound: float


class AnalyseInDB(BaseMongoModel, Analyse):
    ...
