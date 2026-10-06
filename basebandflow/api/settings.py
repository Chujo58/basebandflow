from datetime import datetime, timezone
from pathlib import Path

import yaml
from platformdirs import user_config_dir, user_data_dir

from .errors import SettingsMissing
from .models import Settings

APP = "bbflow"
CONFIG_DIR = Path(user_config_dir(APP, appauthor=False))
DATA_DIR = Path(user_data_dir(APP, appauthor=False))
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"
RUNS_DIR = DATA_DIR / "runs"


def load_settings() -> Settings | None:
    """Returns settings, or None if not set up yet (or file is unusable.)"""
    if not SETTINGS_FILE.exists():
        raise SettingsMissing(
            "Required settings are missing. Please use `bbflow config init`"
        )
    try:
        return Settings(**yaml.safe_load(SETTINGS_FILE.read_text()))
    except Exception as e:  # noqa: BLE001
        raise SettingsMissing(
            f"Cannot open or unpack the settings: {e}. Reset your configuration using `bbflow config init`"
        )


def save_settings(settings: Settings) -> None:
    """Saves the bbflow configuration to a YAML file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS_FILE.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(settings.model_dump()))
    tmp.replace(SETTINGS_FILE)  # atomic swap, no half-written file


# validate_username?
# run_dir creation? maybe something like <eid/timestamp so that we can have some sort of history>? though backwards would also be nice to have.
# day based history.
def run_dir(event_id: str) -> Path:
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%d")
    directory = RUNS_DIR / now_str / event_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory
