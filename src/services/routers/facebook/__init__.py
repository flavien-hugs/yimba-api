from contextlib import asynccontextmanager
from typing import cast

from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination

from src.common.helpers.appdesc import load_app_description, load_permissions
from src.common.helpers.exceptions import setup_exception_handlers
from src.services import FastYimbaAPI, models
from src.services.config import service as service_config
from src.services.config.database import shutdown_db_client, startup_db_client
from .api import router

SETTINGS = cast(service_config.Facebook, service_config.get("facebook"))


@asynccontextmanager
async def lifespan(app: FastYimbaAPI):
    await startup_db_client(app=app, document_models=models.document_models)

    await load_app_description(mongodb_client=app.mongo_db_client)
    await load_permissions(mongodb_client=app.mongo_db_client)

    yield
    await shutdown_db_client(app=app)


app: FastYimbaAPI = FastYimbaAPI(
    lifespan=lifespan, title=SETTINGS.title, docs_url=SETTINGS.docs_url, openapi_url=SETTINGS.openapi_url
)

@app.get("/", include_in_schema=False)
async def read_root() -> RedirectResponse:
    return RedirectResponse(url=f"{SETTINGS.docs_url}")


@app.get(f"{router.prefix}/@ping", tags=["DEFAULT"])
def ping():
    return {"message": "pong !"}


add_pagination(app)
app.include_router(router)
setup_exception_handlers(app)
