from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware


def router_factory(**kwargs) -> APIRouter:
    from yimba_api import NosqlClient
    from yimba_api.config.mongodb import settings as mongo
    from yimba_api.shared import fetch

    router = APIRouter(**kwargs)
    storage = NosqlClient(
        username=mongo.user,
        password=mongo.password,
        hosts=tuple(str.split(mongo.hosts, ",")),
        dbname=mongo.db,
    )
    storage.init()
    setattr(router, "fetch", fetch)
    setattr(router, "storage", storage)
    return router


class FastIreleAPI(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
