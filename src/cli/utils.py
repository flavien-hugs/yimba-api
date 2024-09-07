import uvicorn

from src.services.config import APIBaseSettings


def start_service(name: str, settings: APIBaseSettings, reload: bool = True):
    match settings.APP_ENV.lower():
        case "dev" | "development":
            reload = True
        case "prod" | "production":
            reload = False
        case _:
            raise Exception(f"Invalid environment: {settings.APP_ENV}")

    uvicorn.run(
        f"src.services.routers.{name}:app",
        **{
            "host": settings.API_IP_ADDRESS,
            "port": settings.API_PORT,
            "workers": settings.UVICORN_WORKERS,
            "reload": reload,
        },
    )
