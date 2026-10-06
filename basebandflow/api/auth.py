import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from platformdirs import user_state_dir

from .errors import TokenRefreshFailed, ToolNotFound
from .settings import load_settings

REFRESH_MARGIN = timedelta(minutes=10)
TOKEN_FILE = Path(user_state_dir("bbflow", appauthor=False)) / "chime_frb_tokens.json"


def require_tool(name: str) -> str:  # shutil.which, raises ToolNotFound
    cmd_path = shutil.which(name)
    if not cmd_path:
        raise ToolNotFound(f"{name} is not on PATH")
    return cmd_path


def is_logged_in() -> bool | None:  # canfar probe; None = timeout/unknown
    # First check if canfar exists in CLI:
    require_tool("canfar")
    # Then run the CLI auth info
    completed_process = subprocess.run(
        ["canfar", "ps"], check=False, text=True, timeout=30, capture_output=True
    )
    return completed_process.returncode == 0


def login_interactive() -> int:  # inherits terminal, returns exit code
    completed_process = subprocess.run(["canfar", "login", "--force"], check=False)
    return completed_process.returncode


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


def tokens_need_refresh(token: str | None, margin: timedelta = REFRESH_MARGIN) -> bool:
    remaining = token_time_remaining(token)
    return remaining is None or remaining <= margin


def parse_exports(output: str) -> tuple[str, str]:
    a = re.search(r"CHIME_FRB_ACCESS_TOKEN=(\S+)", output)
    r = re.search(r"CHIME_FRB_REFRESH_TOKEN=(\S+)", output)
    if not (a and r):
        raise TokenRefreshFailed("Couldn't find tokens in refresh output.")
    return a.group(1).strip("'\""), r.group(1).strip("'\"")


def save_tokens(access: str, refresh: str) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = TOKEN_FILE.with_suffix(".tmp")
    fd = os.open(
        tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600
    )  # owner read/write only
    with os.fdopen(fd, "w") as f:
        json.dump({"access": access, "refresh": refresh}, f)
    tmp.replace(TOKEN_FILE)


def load_tokens() -> tuple[str | None, str | None]:
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
    require_tool("frb-api")  # whatever the real command is
    settings = load_settings()
    r = subprocess.run(
        ["frb-api", "generate-tokens", "-u", settings.username],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if r.returncode != 0:
        raise TokenRefreshFailed(
            "Token refresh command failed."
        )  # don't echo output; it may contain secrets
    access, refresh = parse_exports(r.stdout)
    save_tokens(access, refresh)


# def token_env() -> dict[str, str]:
#     access, refresh = load_tokens()
#     env = os.environ.copy()
#     if access:  env["CHIME_FRB_ACCESS_TOKEN"] = access
#     if refresh: env["CHIME_FRB_REFRESH_TOKEN"] = refresh
#     return env


# def ensure_ready_for_launch() -> None           # raises NotLoggedIn / TokenRefreshFailed
