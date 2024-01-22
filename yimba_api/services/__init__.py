from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from yimba_api.config.sentry import settings as sentry_env

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration


sentry_sdk.init(
    dsn=sentry_env.dsn,
    environment=sentry_env.environment,
    release=sentry_env.release,
    integrations=[
        FastApiIntegration(transaction_style="endpoint"),
        StarletteIntegration(transaction_style="endpoint"),
    ],
)


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


class FastYimbaAPI(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
