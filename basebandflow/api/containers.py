import nest_asyncio
from canfar.sessions import Session

from basebandflow.api.models import Container, Settings

# from basebandflow.api.settings import load_settings

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
# Launch the refinement containers

# Check health

# class PipelineContainers:
#     def __init__(self, settings: Settings):
#         if not settings:

#         self.datatrail_container_name: str = ""
#         self.pipeline_container_name: str = ""
#         self.refinement_container_name: str = ""
