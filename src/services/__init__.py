from fastapi import FastAPI, APIRouter

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from src.services.config.sentry import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    release=settings.SENTRY_RELEASE,
    integrations=[
        FastApiIntegration(transaction_style="endpoint"),
        StarletteIntegration(transaction_style="endpoint"),
    ],
)


class FastYimbaAPI(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def router_factory(**kwargs) -> APIRouter:
    router = APIRouter(**kwargs)
    return router
