import json

import typer

from yimba_api.apiclient.encoder import jsonable_encoder
from yimba_api.cli import models
from yimba_api.config import service as config_serv

app = typer.Typer()


@app.command()
def ls(services: list[models.ServiceName] = typer.Argument(...)):
    conf = {}
    for service in services:
        if c := config_serv.get(service.value):
            conf |= {service.value: c}
    typer.echo(json.dumps(jsonable_encoder(conf, exclude_none=True), indent=4))


if __name__ == "__main__":
    app()
