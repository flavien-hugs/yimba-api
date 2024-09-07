import json

import typer

from src import get_logger
from src.cli import models
from src.cli.utils import start_service
from src.services.config import service as service_config

app = typer.Typer()


@app.command()
def ls():
    typer.echo(json.dumps(list(models.ServiceName), indent=4))


@app.command()
def run(
    service: models.ServiceName = typer.Argument(...),
    port: int = typer.Option(None),
    host: str = typer.Option("0.0.0.0"),
    workers: int = typer.Option(1),
):
    config = service_config.get(service.value)
    config.API_PORT = port or config.API_PORT
    config.API_IP_ADDRESS = host or config.API_IP_ADDRESS
    config.UVICORN_WORKERS = workers or config.UVICORN_WORKERS

    logger = get_logger("cli.service", level="debug")
    logger.debug(f"Starting {service.name}")
    logger.debug(f"Config {service.value}")
    logger.debug(f"Config {config}")

    start_service(service.value, config)


if __name__ == "__main__":
    app()
