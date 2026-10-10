from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class Settings(BaseModel):
    username: str
    baseband_path: str | None = None  # None = use the container image's default
    token_refresh_timer: int = 10  # in minutes


@dataclass
class TokenStatus:
    present: bool
    remaining: timedelta | None  # None = missing, malformed, or no exp claim
    needs_refresh: bool  # missing/unreadable, or expires within the margin

    @property
    def expired(self) -> bool:
        return self.remaining is not None and self.remaining.total_seconds() <= 0


@dataclass
class Status:
    settings: Settings | None
    canfar_ok: bool | None  # None = couldn't verify (timeout)
    access_token: TokenStatus
    refresh_token: TokenStatus

    @property
    def tokens_ok(self) -> bool:
        return not self.access_token.needs_refresh

    @property
    def can_refresh(self) -> bool:
        # a refresh only works if the refresh token itself is still usable
        return self.refresh_token.present and not self.refresh_token.expired

    @property
    def ready(self) -> bool:
        return self.settings is not None and self.canfar_ok is True and self.tokens_ok


@dataclass
class RenderedConfig:
    text: str
    parsed: dict
    path: Path
    event_id: str


@dataclass
class Session:
    session_name: str
    session_id: str
    status: str


@dataclass
class Container(Session):
    type: Literal["datatrail", "analysis", "refinement"]


# @dataclass
class LaunchResult(BaseModel):
    event_id: int
    status: Literal["deployed", "rendered", "running", "failed", "completed"]
    config_path: str
    pipeline_id: str
    pipeline_name: str
    config_id: str
    containers: list[Container]
