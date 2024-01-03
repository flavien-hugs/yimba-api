import typer

from yimba_api.cli import config, service

app = typer.Typer(pretty_exceptions_show_locals=False)
app.add_typer(service.app, name="service")
app.add_typer(config.app, name="config")


if __name__ == "__main__":
    app()
