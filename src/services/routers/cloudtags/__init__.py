from typing import cast

from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination

from src.common.helpers.exceptions import setup_exception_handlers
from src.services import FastYimbaAPI
from src.services.config import service as service_config
from .api import router

SETTINGS = cast(service_config.Cloudtags, service_config.get("cloudtags"))

app: FastYimbaAPI = FastYimbaAPI(title=SETTINGS.title, docs_url=SETTINGS.docs_url, openapi_url=SETTINGS.openapi_url)

@app.get("/", include_in_schema=False)
async def read_root() -> RedirectResponse:
    return RedirectResponse(url=f"{SETTINGS.docs_url}")


@app.get(f"{router.prefix}/@ping", tags=["DEFAULT"])
def ping():
    return {"message": "pong !"}


add_pagination(app)
app.include_router(router)
setup_exception_handlers(app)
