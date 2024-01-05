from typing import Optional

from pydantic import BaseModel, validator
from slugify import slugify

from yimba_api import BaseMongoModel


class Role(BaseModel):
    name: str
    slug: Optional[str] = None

    @validator("slug", pre=True, always=True)
    def compute_slug(cls, value, values):  # noqa : B902
        name = values.get("name")
        return slugify(name) if name else value


class RoleInDB(BaseMongoModel, Role):
    ...
