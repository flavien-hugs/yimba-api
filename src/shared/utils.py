from enum import StrEnum
from typing import Optional

from fastapi import BackgroundTasks, status
from slugify import slugify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.common.helpers.exceptions import CustomHTTException
from src.services import models, schemas
from src.shared.error_codes import YimbaApifyErrorCode

analyzer = SentimentIntensityAnalyzer()


async def validate_project(keyword: str, user: Optional[str] = None):
    query = {"slug": slugify(keyword)}
    if user:
        query["user._id"] = user
    if not await models.Project.find_one(query).exists():
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.DOCUMENT_NOT_FOUND,
            message_error=f"Project with name {keyword} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


async def save_analysis(analysis: schemas.CreateAnalyse):
    await models.Analyse(**analysis.model_dump()).create()


async def analyze_data(bg: BackgroundTasks, post_id: str, text: str = ""):
    if not post_id:
        return

    if await models.Analyse.find_one({"post_id": post_id}).exists():
        return

    apc = analyzer.polarity_scores(text)

    analysis = schemas.CreateAnalyse(
        post_id=post_id,
        neutre=apc.get("neu", 0.0),
        negatif=apc.get("neg", 0.0),
        positif=apc.get("pos", 0.0),
        compound=apc.get("compound", 0.0),
    )

    bg.add_task(save_analysis, analysis)


class SortEnum(StrEnum):
    ASC = "asc"
    DESC = "desc"
