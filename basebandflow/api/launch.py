from basebandflow.api.auth import ensure_ready_for_launch
from basebandflow.api.config import render_config
from basebandflow.api.errors import SettingsMissing
from basebandflow.api.models import LaunchResult
from basebandflow.api.settings import require_settings


def launch(event_id: str, *, dry_run: bool) -> LaunchResult:
    # 1. Settings check:
    settings = require_settings

    # 2. Render config:
    configuration = render_config(settings.username, event_id)
    if dry_run:
        return LaunchResult(
            event_id,
            configuration.path,
            "",
            f"{settings.username}-baseband-processing",
            "",
        )

    # 3. Check ready for launch: CANFAR logged in, and tokens that are valid.
    ensure_ready_for_launch()


# def spawn_datatrail_containers()
