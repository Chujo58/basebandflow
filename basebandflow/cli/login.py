import subprocess
import typer
from basebandflow.settings import load_settings, Settings
from dataclasses import dataclass


def run_canfar(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["canfar", *args], capture_output=True, text=True, timeout=30, check=False
    )


def is_logged_in() -> bool:
    return run_canfar("ps").returncode == 0


def login():
    subprocess.run(["canfar", "login", "--force"], check=False)


# Register the commands
def register_login(app: typer.Typer):
    @app.command(
        name="login",
        help="Wrapper for login to CANFAR Science Platform.",
        rich_help_panel="Login",
    )
    def login_command():
        login()


@dataclass
class Status:
    settings: Settings | None
    logged_in: bool

    @property
    def ready(self) -> bool:
        return self.settings is not None and self.logged_in


def get_status() -> Status:
    return Status(settings=load_settings(), logged_in=is_logged_in())
