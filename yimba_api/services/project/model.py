from typing import Optional

from pydantic import BaseModel, validator
from yimba_api import BaseMongoModel
from slugify import slugify


class Project(BaseModel):
    name: str


class ProjectInDB(BaseMongoModel, Project):
    user_id: str
    slug: Optional[str] = None

    @validator("slug", pre=True, always=True)
    def compute_slug(cls, value, values):  # noqa : B902
        name = values.get("name")
        return slugify(name) if name else value
