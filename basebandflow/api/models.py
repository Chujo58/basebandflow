from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    username: str


class Status:
    settings: Settings | None
    canfar_ok: bool | None
    tokens_ok: bool | None


class RenderedConfig:
    text: str
    parsed: dict
    path: Path
    event_id: str


class JobInfo:
    id: str
    name: str
    kind: str
    status: str
