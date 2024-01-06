from fastapi import FastAPI, HTTPException, Request, status

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from fastapi_pagination import add_pagination

from yimba_api.config import service as service_config
from yimba_api.services import FastYimbaAPI
from yimba_api.services.google import api


SETTINGS: service_config.Google = service_config.get("google")


app: FastAPI = FastYimbaAPI(
    title=SETTINGS.title, docs_url=SETTINGS.docs_url, openapi_url=SETTINGS.openapi_url
)
add_pagination(app)
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    def _format_error(err):
        type_value = err.get("type", "").split(".", 1)[-1]
        message = f"Le champ: {err.get('loc', [])[1]} s'attend à une donnée de type '{type_value}'"
        return {
            "field": err.get("loc", [])[1],
            "type": err.get("type", "").split(".", 1)[-1],
            "message": message,
        }

    errors = [_format_error(err) for err in exc.errors()]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"message": errors}),
    )


@app.get("/")
def read_root() -> dict:
    return {
        "app": SETTINGS.title,
        "docs": SETTINGS.docs_url,
        "environment": SETTINGS.env,
    }
