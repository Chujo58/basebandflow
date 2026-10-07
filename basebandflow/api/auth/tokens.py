import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from platformdirs import user_state_dir

from basebandflow import tools
from basebandflow.api.errors import TokenRefreshFailed, ToolNotFound
from basebandflow.api.models import Settings, TokenStatus
from basebandflow.api.settings import require_settings

TOKEN_FILE = Path(user_state_dir("bbflow", appauthor=False)) / "chime_frb_tokens.json"


def token_time_remaining(token: str | None) -> timedelta | None:
    """Time until the token expires (negative if already expired).
    Returns None if the token is missing, malformed, or has no exp claim."""
    if not token:
        return None
    try:
        claims = jwt.decode(token, options={"verify_signature": False})
        exp = claims.get("exp")
        if exp is None:
            return None
        return datetime.fromtimestamp(exp, tz=timezone.utc) - datetime.now(timezone.utc)
    except (jwt.DecodeError, ValueError, TypeError, OverflowError):
        return None


def tokens_need_refresh(token: str | None, margin: timedelta) -> bool:
    remaining = token_time_remaining(token)
    return remaining is None or remaining <= margin


def parse_exports(output: str) -> tuple[str, str]:
    """Parses the output from frb-api to find new tokens."""
    a = re.search(r"CHIME_FRB_ACCESS_TOKEN=(\S+)", output)
    r = re.search(r"CHIME_FRB_REFRESH_TOKEN=(\S+)", output)
    if not (a and r):
        raise TokenRefreshFailed("Couldn't find tokens in refresh output.")
    return a.group(1).strip("'\""), r.group(1).strip("'\"")


def save_tokens(access: str, refresh: str) -> None:
    """Save the tokens to local json file."""
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = TOKEN_FILE.with_suffix(".tmp")
    fd = os.open(
        tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600
    )  # owner read/write only
    with os.fdopen(fd, "w") as f:
        json.dump({"access": access, "refresh": refresh}, f)
    tmp.replace(TOKEN_FILE)


def load_tokens() -> tuple[str | None, str | None]:
    """Loads the tokens either from the environment (first check), or the stored json file."""
    # environment wins, so a user who exports them manually still works
    access = os.environ.get("CHIME_FRB_ACCESS_TOKEN")
    refresh = os.environ.get("CHIME_FRB_REFRESH_TOKEN")
    if access and refresh:
        return access, refresh
    try:
        data = json.loads(TOKEN_FILE.read_text())
        return data.get("access"), data.get("refresh")
    except (OSError, ValueError):
        return None, None


def refresh_tokens() -> None:
    # require_tool("frb-api")
    settings = require_settings()
    if not sys.stdin.isatty():
        raise TokenRefreshFailed(
            "Token refresh needs a password; run `bbflow login` in a terminal."
        )
    try:
        r = tools.frb_api(
            "generate-tokens",
            "-u",
            settings.username,
            stdout=tools.subprocess.PIPE,
            text=True,
            timeout=300,
        )
    except tools.subprocess.TimeoutExpired:
        raise TokenRefreshFailed("Token refresh timed out.") from None
    if r.returncode != 0:
        raise TokenRefreshFailed("Token refresh failed (wrong password?).")

    access, refresh = parse_exports(r.stdout)
    save_tokens(access, refresh)
    _export_to_env(access, refresh)


def _export_to_env(access: str, refresh: str) -> None:
    """Export the tokens to the environment"""
    os.environ["CHIME_FRB_ACCESS_TOKEN"] = access
    os.environ["CHIME_FRB_REFRESH_TOKEN"] = refresh
