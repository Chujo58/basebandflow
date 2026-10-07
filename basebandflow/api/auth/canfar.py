from basebandflow import tools
from basebandflow.api.errors import ToolNotFound


def is_logged_in() -> bool | None:
    """True/False, or None if it couldn't be verified (timeout)."""
    try:
        r = tools.canfar(
            "ps",
            stdin=tools.subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except ToolNotFound:
        return False
    except tools.subprocess.TimeoutExpired:
        return None
    return r.returncode == 0


def login_interactive() -> int:  # inherits terminal, returns exit code
    r = tools.canfar("login", "--force")
    return r.returncode
