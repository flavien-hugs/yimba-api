from typing import Any, Dict, Optional

from beanie import before_event, Document, Indexed
from beanie.odm.actions import EventTypes
from pymongo import IndexModel, TEXT
from slugify import slugify

from src.services.schemas import CollectData, CreateAnalyse, CreateProject
from .mixins import TimestampModel


class Analyse(Document, CreateAnalyse, TimestampModel):
    pass


class Facebook(Document, CollectData, TimestampModel):
    pass


class Google(Document, CollectData, TimestampModel):
    pass


class Instagram(Document, CollectData, TimestampModel):
    pass


class Youtube(Document, CollectData, TimestampModel):
    pass


class Twitter(Document, CollectData, TimestampModel):
    pass


class Tiktok(Document, CollectData, TimestampModel):
    pass


class Project(Document, CreateProject, TimestampModel):
    user: Dict[str, Any]
    slug: Optional[Indexed(str, unique=True, sparse=True)] = None

    class Settings:
        indexes = [
            IndexModel(
                keys=[
                    ("name", TEXT),
                    ("description", TEXT),
                    ("slug", TEXT),
                ]
            )
        ]

    @before_event(EventTypes.INSERT)
    async def generate_unique_slug(self, **kwargs):
        new_slug_value = slugify(self.name)
        user_id = self.user.get("id")
        if await Project.find_one({"user": user_id, "slug": new_slug_value}).exists() is True:
            raise
        else:
            self.slug = new_slug_value
