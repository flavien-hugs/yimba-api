from typing import cast

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.common.helpers.exceptions import setup_exception_handlers
from src.services import FastYimbaAPI
from src.services.config import service as service_config
from .api import router

SETTINGS = cast(service_config.Rapport, service_config.get("rapport"))

app: FastAPI = FastYimbaAPI(title=SETTINGS.title, docs_url=SETTINGS.docs_url, openapi_url=SETTINGS.openapi_url)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(router)
setup_exception_handlers(app)


@app.get("/", include_in_schema=False)
async def read_root() -> RedirectResponse:
    return RedirectResponse(url=f"{SETTINGS.docs_url}")


@app.get("/@ping", tags=["DEFAULT"])
def ping():
    return {"message": "pong !"}
