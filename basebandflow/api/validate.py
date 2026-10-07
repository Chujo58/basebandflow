import re

from basebandflow.api.errors import InvalidEventId, InvalidUsername

_EVENT_ID_RE = re.compile(r"[0-9]+")  # ASCII digits only
_USERNAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


def validate_event_id(event_id: str) -> str:
    """Return the event ID unchanged if valid, else raise InvalidEventId."""
    event_id = event_id.strip()  # forgive stray whitespace from copy/paste
    if not _EVENT_ID_RE.fullmatch(event_id):
        raise InvalidEventId(f"Event ID must be digits only (got {event_id!r}).")
    return event_id


def validate_username(username: str) -> str:
    username = username.strip()
    if not _USERNAME_RE.fullmatch(username):
        raise InvalidUsername(
            f"Username may only contain letters, digits, '_', '.', '-' (got {username!r})."
        )
    return username
