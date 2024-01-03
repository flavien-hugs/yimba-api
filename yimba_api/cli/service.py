import json

import typer

from yimba_api import get_logger
from yimba_api.cli import models
from yimba_api.cli.utils import start_service
from yimba_api.config import service as service_config

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
    config.ip = host or config.ip
    config.port = port or config.port
    config.workers = workers or config.workers

    logger = get_logger("cli.service", level=config.log_level.value)
    logger.debug(f"Starting {service.name}")
    logger.debug(f"Config {service.value}")
    logger.debug(f"Config {config}")

    start_service(service.value, config)


if __name__ == "__main__":
    app()
