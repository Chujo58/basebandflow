# basebandflow/settings.py
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir
from pydantic import BaseModel
import yaml

APP = "bbflow"
CONFIG_DIR = Path(user_config_dir(APP, appauthor=False))
DATA_DIR = Path(user_data_dir(APP, appauthor=False))
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"
RUNS_DIR = DATA_DIR / "runs"  # rendered configs go here


class Settings(BaseModel):
    username: str


def load_settings() -> Settings | None:
    """Return settings, or None if not set up yet (or file is unusable)."""
    if not SETTINGS_FILE.exists():
        return None
    try:
        return Settings(**yaml.safe_load(SETTINGS_FILE.read_text()))
    except Exception:
        return None  # corrupt/incomplete: treat as "not set up"


def save_settings(settings: Settings) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS_FILE.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(settings.model_dump()))
    tmp.replace(SETTINGS_FILE)  # atomic swap, no half-written file
