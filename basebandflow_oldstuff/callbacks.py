"""Application callbacks used by the command-line interface."""

from dataclasses import dataclass
import subprocess

from basebandflow.settings import Settings, load_settings


def login() -> None:
    """Start the CANFAR login flow."""
    subprocess.run(["canfar", "login", "--force"], check=False)


def run_canfar(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["canfar", *args], capture_output=True, text=True, timeout=30, check=False
    )


def is_logged_in() -> bool:
    return run_canfar("ps").returncode == 0


@dataclass
class Status:
    settings: Settings | None
    logged_in: bool

    @property
    def ready(self) -> bool:
        return self.settings is not None and self.logged_in


def get_status() -> Status:
    return Status(settings=load_settings(), logged_in=is_logged_in())


def validate_launch(dry_run: bool) -> Settings:
    """Return launch settings or raise when the environment is not ready."""
    settings = load_settings()
    if settings is None:
        raise RuntimeError("No username set. Configure bbflow before launching.")
    if not dry_run and not is_logged_in():
        raise PermissionError("Not logged in to CANFAR. Run `bbflow login` first.")
    return settings
