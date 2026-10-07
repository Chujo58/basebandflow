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


# Launch the analysis containers
# def spawn_analysis_container(settings: Settings, tokens) -> tuple[Container]:
#     payload = {
#     "name": "clegue-baseband",
#     "image": "images.canfar.net/chimefrb/baseband-analysis:latest",
#     "cores": 2,
#     "ram": 8,
#     "kind": "headless",
#     "cmd": "workflow",
#     "args": "run --site=canfar baseband-clegue",
#     "env": {
#         "SITE": "canfar",
#         "CHIME_FRB_ACCESS_TOKEN": CHIME_FRB_ACCESS_TOKEN,
#         "CHIME_FRB_REFRESH_TOKEN": CHIME_FRB_REFRESH_TOKEN,
#         "PYTHONPATH": BASEBAND_PATH,
#         # 'PYTHONPATH': '/arc/home/user/baseband-analysis/' # you can set this if you want to run your local branch on this headless session
#     },
#     "replicas": 10,
# }
# Launch the refinement containers

# Check health

# class PipelineContainers:
#     def __init__(self, settings: Settings):
#         if not settings:

#         self.datatrail_container_name: str = ""
#         self.pipeline_container_name: str = ""
#         self.refinement_container_name: str = ""
