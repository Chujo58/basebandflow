from datetime import timedelta

from basebandflow.api.auth.canfar import is_logged_in
from basebandflow.api.auth.tokens import (
    load_tokens,
    refresh_tokens,
    token_time_remaining,
    tokens_need_refresh,
)
from basebandflow.api.errors import InvalidTokens, NotLoggedIn, TokenRefreshFailed
from basebandflow.api.settings import require_settings
from basebandflow.models import TokenStatus
from basebandflow.tools import require_tool


def tokens_valid() -> bool:
    settings = require_settings()
    margin = timedelta(minutes=settings.token_refresh_timer)
    access, _ = load_tokens()
    return not tokens_need_refresh(access, margin)


def refresh_and_verify() -> None:
    """Refresh (prompts for a password), then confirm the result. Call from the CLI, not from launch()."""
    refresh_tokens()
    if not tokens_valid():
        raise TokenRefreshFailed("Tokens are still expired after refresh.")


def ensure_ready_for_launch() -> None:
    require_tool("workflow")
    logged_in = is_logged_in()
    if logged_in is None:
        raise NotLoggedIn(
            "Couldn't reach CANFAR to verify your login. Check your connection and retry."
        )
    if not logged_in:
        raise NotLoggedIn("Not logged in to CANFAR. Run `bbflow login`.")
    if not tokens_valid():
        raise InvalidTokens(
            "CHIME/FRB tokens are expired or about to expire."
        )  # no refresh here


def _token_status(token: str | None, margin: timedelta) -> TokenStatus:
    return TokenStatus(
        present=bool(token),
        remaining=token_time_remaining(token),
        needs_refresh=tokens_need_refresh(token, margin),
    )


def check_tokens() -> tuple[TokenStatus, TokenStatus]:
    settings = require_settings()
    access, refresh = load_tokens()
    return _token_status(
        access, timedelta(minutes=settings.token_refresh_timer)
    ), _token_status(refresh, timedelta(minutes=settings.token_refresh_timer))
