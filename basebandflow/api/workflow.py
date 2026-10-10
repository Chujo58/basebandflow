from basebandflow import tools
from basebandflow.api.settings import load_settings


def abort(config_id: str):
    settings = load_settings()
    config_name = f"{settings.username}-baseband-processing"
    return tools.workflow("configs", "stop", config_name, config_id)


def parse_deploy(output: str):
    name = None
    config_id = None
    pipelines: list[str] = []
    in_pipelines = False

    for raw in output.splitlines():
        line = raw.strip(" \t┃│")  # drop the table's side borders
        if line.startswith("Config deployed:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("config:"):
            config_id = line.split(":", 1)[1].strip()
        elif line.startswith("pipelines:"):
            in_pipelines = True
        elif (
            in_pipelines and line.isalnum()
        ):  # IDs are alphanumeric; border lines and blanks aren't
            pipelines.append(line)
    return name, config_id, pipelines


def deploy(configuration_path: str):
    r = tools.workflow(
        "configs",
        "deploy",
        configuration_path,
        stdin=tools.subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return parse_deploy(r.stdout)


def stop(config_id: str, config_name: str):
    return tools.workflow("configs", "stop", config_name, config_id)


def status(pipeline_id: str):
    return tools.workflow(
        "pipelines", "ps", pipeline_id, stderr=tools.subprocess.DEVNULL
    )
