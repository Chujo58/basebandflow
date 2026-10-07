# import re

import nest_asyncio
from canfar.sessions import Session

from basebandflow import tools
from basebandflow.api.models import Container, Settings

nest_asyncio.apply()
s = Session()

# _STATUS_RE = re.compile(r"^\s*Status\s{2,}(\S.*?)\s*$", re.MULTILINE)


# Launch the datatrail containers
def spawn_datatrail_container(settings: Settings) -> tuple[Container]:
    payload = {
        "name": "baseband-datatrail",  # name of the session
        "image": "images.canfar.net/chimefrb/baseband-analysis:latest",  # image you're pulling #Try using chimefrb-public/baseband-analysis:latest if this image container does not work
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
            f"baseband-{settings.username}-datatrail",
            "datatrail",
            True,
        )
        containers.append(container)
    return containers


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
        "image": "images.canfar.net/chimefrb/baseband-analysis:latest",
        "cores": 2,
        "ram": 8,
        "kind": "headless",
        "cmd": "workflow",
        "args": f"run --site=canfar baseband-{settings.username}",
        "env": env,
        "replicas": 10,
    }

    session_ids = s.create(**payload)
    containers = []
    for sid in session_ids:
        container = Container(
            payload.get("name"),
            sid,
            f"baseband-{settings.username}",
            "analysis",
            True,
        )
        containers.append(container)
    return containers


# Launch the refinement containers
def spawn_refinement_container(
    settings: Settings, access_token: str, refresh_token: str
) -> tuple[Container]:
    env = build_container_env(settings, access_token, refresh_token)

    payload = {
        "name": "baseband-refinement",
        "image": "images.canfar.net/chimefrb/baseband-analysis:latest",
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
            f"baseband-{settings.username}-brightest",
            "refinement",
            True,
        )
        containers.append(container)
    return containers


# Check health
def check_health(sid: str) -> str | None:
    session_info = s.info(sid)
    if session_info is not None:
        session_info = session_info[0]  # grab the first one, this returns a list.

    return session_info.get("status")


def check_existing_containers() -> list[str]:
    sessions = s.fetch(kind="headless", status="Running")
    names = [session.get("name") for session in sessions]

    return names
