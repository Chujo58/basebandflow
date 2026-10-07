import nest_asyncio
from canfar.sessions import Session

from basebandflow.api.models import Container, Settings

nest_asyncio.apply()
s = Session()


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
    session_ids = s.create(payload)
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

    session_ids = s.create(payload)
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

    session_ids = s.create(payload)
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

# class PipelineContainers:
#     def __init__(self, settings: Settings):
#         if not settings:

#         self.datatrail_container_name: str = ""
#         self.pipeline_container_name: str = ""
#         self.refinement_container_name: str = ""
