from datetime import datetime
from pathlib import Path

import yaml
from platformdirs import user_config_dir, user_data_dir
from pydantic import ValidationError

from basebandflow.api.errors import SettingsCorrupt, SettingsMissing
from basebandflow.models import Settings

APP = "bbflow"
CONFIG_DIR = Path(user_config_dir(APP, appauthor=False))
DATA_DIR = Path(user_data_dir(APP, appauthor=False))
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"
RUNS_DIR = DATA_DIR / "runs"


def load_settings() -> Settings | None:
    """Returns settings, or None if not set up yet (or file is unusable.)"""
    if not SETTINGS_FILE.exists():
        return None
    try:
        data = yaml.safe_load(SETTINGS_FILE.read_text(encoding="utf-8"))
        return Settings(**(data or {}))
    except (OSError, yaml.YAMLError, ValidationError, TypeError) as e:
        raise SettingsCorrupt(
            f"Can't read {SETTINGS_FILE}. Reset it with `bbflow config init`."
        ) from e


def save_settings(settings: Settings) -> None:
    """Saves the bbflow configuration to a YAML file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS_FILE.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(settings.model_dump(exclude_none=True)))
    tmp.replace(SETTINGS_FILE)  # atomic swap, no half-written file


def require_settings() -> Settings:
    """For code that can't proceed without settings."""
    settings = load_settings()
    if settings is None:
        raise SettingsMissing("No username set. Run `bbflow config init`.")
    return settings


def run_dir(event_id: str) -> Path:
    # Get local time and create a directory for the run.
    now = datetime.now().astimezone()
    directory = (
        RUNS_DIR / now.strftime("%Y-%m-%d") / f"{now.strftime('%H%M%S')}_{event_id}"
    )
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def list_runs(event_id: str | None = None) -> list[Path]:
    """Newest first. Optionally only runs for one event."""
    pattern = f"*/*_{event_id}" if event_id else "*/*"
    return sorted(RUNS_DIR.glob(pattern), reverse=True)
