from pydantic import Field

from yimba_api.config import YimbaBaseSettings


class MongodbSettings(YimbaBaseSettings):
    db: str = Field(..., env="MONGO_DB")
    port: int = Field(..., env="MONGO_PORT")
    user: str = Field(..., env="MONGO_USER")
    hosts: str = Field(..., env="MONGO_HOSTS")
    password: str = Field(..., env="MONGO_PASSWORD")


settings = MongodbSettings()
