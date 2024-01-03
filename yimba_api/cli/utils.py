import uvicorn

from yimba_api.config import APIBaseSettings


def start_service(name: str, settings: APIBaseSettings, reload: bool = True):
    match settings.env.lower():
        case "dev" | "development":
            reload = True
        case "prod" | "production":
            reload = False
        case _:
            raise Exception(f"Invalid environment: {settings.env}")

    uvicorn.run(
        f"yimba_api.services.{name}:app",
        **{
            "host": str(settings.ip),
            "port": settings.port,
            "workers": settings.workers,
            "log_level": settings.log_level.lower(),
            "reload": reload,
        },
    )
