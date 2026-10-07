import typer

from basebandflow.api.config import validate_username
from basebandflow.api.errors import SettingsMissing
from basebandflow.api.models import Settings
from basebandflow.api.settings import SETTINGS_FILE, load_settings, save_settings
from basebandflow.cli.ui import console

config_app = typer.Typer(help="Configuration of basebandflow", no_args_is_help=True)


def run_init() -> Settings:
    canfar_username = console.input("Enter your CANFAR username: ")
    validated_username = validate_username(canfar_username)
    new_settings = Settings(username=validated_username)

    save_settings(new_settings)
    console.print("[green]Saved configuration![/green]")
    return new_settings


@config_app.command()
def init():
    settings = run_init()
    if not settings.username:
        raise SettingsMissing("Missing username")


@config_app.command()
def show():
    settings = load_settings()
    if not settings:
        console.print("Not setup")

    console.print(f"CANFAR Username: {settings.username}")


@config_app.command()
def path():
    console.print(f"Configuration is saved at: {SETTINGS_FILE}")


def register(app: typer.Typer):
    app.add_typer(config_app, name="config")
