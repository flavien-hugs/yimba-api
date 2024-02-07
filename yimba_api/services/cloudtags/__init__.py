from fastapi import FastAPI, HTTPException, Request, status

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from yimba_api.services import FastYimbaAPI
from yimba_api.services.cloudtags import api
from yimba_api.config import service as service_config


SETTINGS: service_config.Cloudtags = service_config.get("cloudtags")


app: FastAPI = FastYimbaAPI(
    title=SETTINGS.title, docs_url=SETTINGS.docs_url, openapi_url=SETTINGS.openapi_url
)
app.include_router(api.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"message": str(exc.detail)}),
    )


@app.exception_handler(Exception)
async def server_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"message": str(exc)}),
    )


@app.get("/")
def read_root() -> dict:
    return {
        "app": SETTINGS.title,
        "docs": SETTINGS.docs_url,
        "environment": SETTINGS.env,
    }
