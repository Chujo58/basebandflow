from typing import Literal

import nest_asyncio
from canfar.sessions import Session

from basebandflow.api.auth import ensure_ready_for_launch
from basebandflow.api.auth.tokens import load_tokens
from basebandflow.api.settings import require_settings
from basebandflow.models import Container, Settings

nest_asyncio.apply()
s = Session()

# _STATUS_RE = re.compile(r"^\s*Status\s{2,}(\S.*?)\s*$", re.MULTILINE)
baseband_analysis_image = "images.canfar.net/chimefrb-public/baseband-analysis:latest"


# Launch the datatrail containers
def spawn_datatrail_container(settings: Settings) -> tuple[Container]:
    payload = {
        "name": "baseband-datatrail",  # name of the session
        "image": baseband_analysis_image,  # image you're pulling #Try using chimefrb-public/baseband-analysis:latest if this image container does not work
        "cores": 4,  # data staging now supports multithreaded pulling
        "ram": 2,
        "kind": "headless",
        "cmd": "workflow",
        "args": f"run --site=canfar baseband-{settings.username}-datatrail",  # the last args is the bucket name!!!!
        "env": {"SITE": "canfar"},
        "replicas": 2,
    }
    session_ids = s.create(**payload)
    containers = []
    for sid in session_ids:
        container = Container(
            payload.get("name"),
            sid,
            "pending",
            "datatrail",
        )
        containers.append(container)
    return containers


def prune_datatrail_container() -> bool:
    res = s.destroy_with(prefix="baseband-datatrail", status=None)
    return bool(res) and all(res.values())


def build_container_env(
    settings: Settings, access_token: str, refresh_token: str
) -> dict:
    env = {
        "SITE": "canfar",
        "CHIME_FRB_ACCESS_TOKEN": access_token,
        "CHIME_FRB_REFRESH_TOKEN": refresh_token,
        # 'PYTHONPATH': '/arc/home/user/baseband-analysis/' # you can set this if you want to run your local branch on this headless session
    }

    if settings.baseband_path is not None:
        env.update({"PYTHONPATH": settings.baseband_path})
    return env


# Launch the analysis containers
def spawn_analysis_container(
    settings: Settings, access_token: str, refresh_token: str
) -> tuple[Container]:
    env = build_container_env(settings, access_token, refresh_token)

    payload = {
        "name": "baseband-analysis",
        "image": baseband_analysis_image,
        "cores": 2,
        "ram": 16,
        "kind": "headless",
        "cmd": "workflow",
        "args": f"run --site=canfar baseband-{settings.username}",
        "env": env,
        "replicas": 5,
    }

    session_ids = s.create(**payload)
    containers = []
    for sid in session_ids:
        container = Container(
            payload.get("name"),
            sid,
            "pending",
            "analysis",
        )
        containers.append(container)
    return containers


def prune_analysis_container() -> bool:
    res = s.destroy_with(prefix="baseband-analysis", status=None)
    return bool(res) and all(res.values())


# Launch the refinement containers
def spawn_refinement_container(
    settings: Settings, access_token: str, refresh_token: str
) -> tuple[Container]:
    env = build_container_env(settings, access_token, refresh_token)

    payload = {
        "name": "baseband-refinement",
        "image": baseband_analysis_image,
        "cores": 8,
        "ram": 32,
        "kind": "headless",
        "cmd": "workflow",
        "args": f"run --log-level=INFO --site=canfar baseband-{settings.username}-brightest",
        "env": env,
        "replicas": 1,
    }

    session_ids = s.create(**payload)
    containers = []
    for sid in session_ids:
        container = Container(
            payload.get("name"),
            sid,
            "pending",
            "refinement",
        )
        containers.append(container)
    return containers


def prune_refinement_container() -> bool:
    res = s.destroy_with(prefix="baseband-refinement", status=None)
    return bool(res) and all(res.values())


# Check health
def check_health(sid: list[str]) -> list[str] | None:
    session_info = s.info(sid)
    if session_info is None:
        return

    return [sinf.get("status") for sinf in session_info]


def delete_container(ids: str | list[str]) -> bool:
    res = s.destroy(ids)
    return all(res)


def prune_containers(session_type: Literal["datatrail", "analysis", "refinement"]):
    if session_type == "datatrail":
        return prune_datatrail_container()
    if session_type == "analysis":
        return prune_analysis_container()
    if session_type == "refinement":
        return prune_refinement_container()


def initialize_session_container(session_type) -> list[Container]:
    settings = require_settings()

    current_containers = list(
        filter(lambda x: x.type == session_type, list_headless_containers())
    )
    if session_type == "datatrail":
        if 0 < len(current_containers) <= 2:
            prune_containers(session_type)

        return spawn_datatrail_container(settings)

    ensure_ready_for_launch()
    access, refresh = load_tokens()

    if session_type == "analysis":
        if 0 < len(current_containers) <= 10:
            prune_containers(session_type)

        return spawn_analysis_container(settings, access, refresh)

    if session_type == "refinement":
        if 0 < len(current_containers) <= 1:
            prune_containers(session_type)

        return spawn_refinement_container(settings, access, refresh)


def list_headless_containers() -> list[Container]:
    sessions = s.fetch(kind="headless")
    containers = []
    for session in sessions:
        cont_type = session.get("name").split("-")[1]
        container = Container(
            session.get("name"), session.get("id"), session.get("status"), cont_type
        )
        containers.append(container)

    containers.sort(key=lambda x: x.session_name)

    return containers
