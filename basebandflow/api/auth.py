import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from platformdirs import user_state_dir

from basebandflow.api.errors import (
    InvalidTokens,
    NotLoggedIn,
    SettingsMissing,
    TokenRefreshFailed,
    ToolNotFound,
)
from basebandflow.api.models import TokenStatus
from basebandflow.api.settings import load_settings

REFRESH_MARGIN = timedelta(minutes=10)
TOKEN_FILE = Path(user_state_dir("bbflow", appauthor=False)) / "chime_frb_tokens.json"


def require_tool(name: str) -> str:  # shutil.which, raises ToolNotFound
    cmd_path = shutil.which(name)
    if not cmd_path:
        raise ToolNotFound(f"{name} is not on PATH")
    return cmd_path


def is_logged_in() -> bool | None:
    """True/False, or None if it couldn't be verified (timeout)."""
    if shutil.which("canfar") is None:
        return False
    try:
        r = subprocess.run(
            ["canfar", "ps"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    return r.returncode == 0


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
    require_tool("frb-api")
    settings = load_settings()
    if settings is None:
        raise SettingsMissing("No username set. Run `bbflow config init`.")
    if not sys.stdin.isatty():
        raise TokenRefreshFailed(
            "Token refresh needs a password; run `bbflow login` in a terminal."
        )
    try:
        r = subprocess.run(
            ["frb-api", "generate-tokens", "-u", settings.username],
            stdout=subprocess.PIPE,  # capture the export lines; stdin/stderr stay on the terminal
            text=True,
            timeout=300,  # the user is typing, so be generous
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise TokenRefreshFailed("Token refresh timed out.") from None
    if r.returncode != 0:
        raise TokenRefreshFailed("Token refresh failed (wrong password?).")
    access, refresh = parse_exports(r.stdout)
    save_tokens(access, refresh)
    _export_to_env(access, refresh)


def ensure_tokens_valid() -> None:
    access, _ = load_tokens()
    if not tokens_need_refresh(access):
        return
    refresh_tokens()
    access, _ = load_tokens()
    if tokens_need_refresh(access):
        raise TokenRefreshFailed("Tokens are still expired after refresh.")


def ensure_ready_for_launch() -> None:
    require_tool("canfar")
    require_tool("workflow")

    logged_in = is_logged_in()
    if logged_in is None:
        raise NotLoggedIn(
            "Couldn't reach CANFAR to verify your login. Check your connection and retry."
        )
    if not logged_in:
        raise NotLoggedIn("Not logged in to CANFAR. Run `bbflow login`.")

    ensure_tokens_valid()


def _export_to_env(access: str, refresh: str) -> None:
    os.environ["CHIME_FRB_ACCESS_TOKEN"] = access
    os.environ["CHIME_FRB_REFRESH_TOKEN"] = refresh


def _token_status(token: str | None) -> TokenStatus:
    return TokenStatus(
        present=bool(token),
        remaining=token_time_remaining(token),
        needs_refresh=tokens_need_refresh(token),
    )


def check_tokens() -> tuple[TokenStatus, TokenStatus]:
    access, refresh = load_tokens()
    return _token_status(access), _token_status(refresh)
