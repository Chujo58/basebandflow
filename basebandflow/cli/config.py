from typing import Annotated

import typer
from rich.markup import escape

from basebandflow.api.errors import SettingsMissing
from basebandflow.api.settings import (
    SETTINGS_FILE,
    load_settings,
    require_settings,
    save_settings,
)
from basebandflow.api.validate import validate_username
from basebandflow.cli.ui import console
from basebandflow.models import Settings

config_app = typer.Typer(help="Configuration of basebandflow", no_args_is_help=True)


def run_init() -> Settings:
    try:
        existing = load_settings()
    except SettingsMissing:  # includes corrupt: start fresh
        existing = None

    name = typer.prompt(
        "CANFAR username", default=existing.username if existing else None
    )
    username = validate_username(name)
    settings = (
        existing.model_copy(update={"username": username})
        if existing
        else Settings(username=username)
    )
    save_settings(settings)
    console.print("[green]✔ Saved configuration[/green]")
    return settings


@config_app.command()
def init():
    settings = run_init()
    if not settings.username:
        raise SettingsMissing("Missing username")


def parameter_complete():
    return "username", "baseband_path", "refresh_timer"


@config_app.command()
def set(
    parameter: Annotated[
        str,
        typer.Argument(
            help=f"Choose between {', '.join(parameter_complete())} to update the configuration",
            autocompletion=parameter_complete,
        ),
    ],
):
    try:
        existing = load_settings()
    except SettingsMissing:  # includes corrupt: start fresh
        existing = None

    if parameter == "username":
        name = typer.prompt(
            "CANFAR username", default=existing.username if existing else None
        )
        username = validate_username(name)
        settings = (
            existing.model_copy(update={"username": username})
            if existing
            else Settings(username=username)
        )
        save_settings(settings)
        console.print("[green]✔ Saved configuration[/green]")

    if parameter == "baseband_path":
        path = typer.prompt(
            "baseband-analysis PATH on CANFAR",
            default=existing.baseband_path if existing else None,
        )

        settings = (
            existing.model_copy(update={"baseband_path": path})
            if existing
            else Settings(baseband_path=path)
        )
        save_settings(settings)
        console.print("[green]✔ Saved configuration[/green]")

    if parameter == "refresh_timer":
        time = typer.prompt(
            "How many minutes until tokens need to be refreshed?",
            default=existing.token_refresh_timer if existing else None,
            value_proc=int,
        )

        settings = existing.model_copy(
            update={"token_refresh_timer": time}
            if existing
            else Settings(token_refresh_timer=time)
        )
        save_settings(settings)
        console.print("[green]✔ Saved configuration[/green]")


@config_app.command()
def show():
    settings = require_settings()

    console.print(
        f"[dim]CANFAR username:[/dim] [cyan]{escape(settings.username)}[/cyan]"
    )
    console.print(
        f"[dim]baseband path:  [/dim] [cyan]{escape(settings.baseband_path or '(default)')}[/cyan]"
    )


@config_app.command()
def path():
    console.print(f"Configuration is saved at: {SETTINGS_FILE}")


def register(app: typer.Typer):
    app.add_typer(config_app, name="config")
