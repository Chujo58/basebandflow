from basebandflow.api.auth import check_tokens, is_logged_in
from basebandflow.api.errors import SettingsMissing
from basebandflow.api.models import Status
from basebandflow.api.settings import load_settings


def get_status() -> Status:
    access, refresh = check_tokens()
    try:
        settings = load_settings()
    except SettingsMissing:
        settings = None

    return Status(
        settings=settings,
        canfar_ok=is_logged_in(),
        access_token=access,
        refresh_token=refresh,
    )
