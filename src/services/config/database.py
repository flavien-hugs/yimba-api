import logging
from typing import List, Type

from beanie import Document, init_beanie

from src.common.helpers.mongodb import mongodb_client
from src.services import FastYimbaAPI
from src.services.config.base import settings

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(message)s", level=logging.INFO)


async def startup_db_client(app: FastYimbaAPI, document_models: List[Type[Document]]):
    client = await mongodb_client(settings.MONGODB_URI)
    app.mongo_db_client = client
    await init_beanie(database=client[settings.MONGO_DB], document_models=document_models)

    logger.info("--> Database init successfully !")


async def shutdown_db_client(app: FastYimbaAPI):
    app.mongo_db_client.close()
    logger.info("--> Database closed successfully !")
