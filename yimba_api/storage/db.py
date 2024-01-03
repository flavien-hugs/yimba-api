from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, validator


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class NosqlClient:
    def __init__(
        self,
        username: str = None,
        password: str = None,
        hosts: tuple[str] = ("localhost:27017",),
        dbname: str = "likya",
        **extra,
    ) -> None:
        self.username = username
        self.password = password
        self.hosts = hosts
        self.dbname = dbname
        self.extra = extra
        self._client: AsyncIOMotorClient = None

    @property
    def mongodburl(self):
        url = f"mongodb://{','.join(self.hosts).strip(',')}/?"
        extra = {"retryWrites": "true", "w": "majority", **self.extra}
        for key, value in extra.items():
            url += f"{key}={value}&"
        return url.strip("&")

    def init(self):
        if self._client is None:
            self._client = AsyncIOMotorClient(
                self.mongodburl, username=self.username, password=self.password
            )
        return self._client

    @property
    def db(self):
        return self.init()[self.dbname]

    def close(self):
        self._client.close()

    def is_async_method(self, collection: str, method: str) -> bool:
        return getattr(
            getattr(self.db[collection], method),
            "is_async_method",
            False,
        )

    async def __call__(self, collection: str, method: str, *args, **kwd):
        assert self.is_async_method(collection, method), (
            f"Unsupported method try: "
            f"{self.__class__.__name__}.db.{collection}.{method}"
        )
        return await getattr(self.db[collection], method)(*args, **kwd)


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @validator("created_at", "updated_at", pre=True, always=True)
    def default_datetime(cls, value: datetime) -> datetime:  # noqa : B902
        return value or datetime.now()


class BaseMongoModel(DateTimeModelMixin):
    id: str = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    async def save(self, mongo: NosqlClient):
        return await mongo.db[type(self).__name__].insert_one(jsonable_encoder(self))

    async def update(self, mongo: NosqlClient):
        return await mongo.db[type(self).__name__].update_one(
            {"_id": str(self.id)}, {"$set": jsonable_encoder(self)}
        )

    @classmethod
    async def update_one(cls, mongo: NosqlClient, oid: str, **kwargs):
        return await mongo.db[cls.__name__].update_one({"_id": oid}, {"$set": kwargs})

    async def delete(self, mongo: NosqlClient):
        return await mongo.db[type(self).__name__].delete_one({"_id": str(self.id)})

    @classmethod
    async def delete_one(cls, mongo: NosqlClient, oid: str):
        return await mongo.db[cls.__name__].delete_one({"_id": oid})

    @classmethod
    async def find_one(cls, mongo: NosqlClient, *args, **kwargs):
        if (
            result := await mongo.db[cls.__name__].find_one(*args, **kwargs)
        ) is not None:
            return cls(**result)

    @classmethod
    async def find(cls, mongo: NosqlClient, *args, **kwargs):
        async for doc in mongo.db[cls.__name__].find(*args, **kwargs).sort(
            {"created_at": -1}
        ):
            yield cls(**doc)

    @classmethod
    async def count(cls, mongo: NosqlClient, filter=None, session=None, **kwargs):
        return await mongo.db[cls.__name__].count_documents(
            (filter or {}), session=session, **kwargs
        )
