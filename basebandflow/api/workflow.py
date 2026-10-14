from collections import Counter
from datetime import datetime

from basebandflow import tools
from basebandflow.api.errors import BBFlowError
from basebandflow.api.settings import load_settings
from basebandflow.models import PipelineStatus

SYMBOLS = {"✅": "done", "🏃": "running", "📅": "queued", "⚪": "waiting"}


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
        "pipelines",
        "ps",
        pipeline_id,
        text=True,
        capture_output=True,
    )


def _parse_time(text: str) -> datetime | None:
    try:
        return datetime.strptime(text, "%m-%d-%Y, %H:%M:%S")
    except ValueError:
        return None


def parse_pipeline_ps(output: str) -> PipelineStatus:
    title = ""
    fields: dict[str, str] = {}
    groups: dict[str, Counter] = {}
    in_steps = False

    for raw in output.splitlines():
        line = raw.strip()
        if line.startswith("┃") and line.endswith("┃"):
            title = line.strip("┃ ").removeprefix("Pipeline:").strip()
            continue
        if not (line.startswith("│") and line.endswith("│")):
            continue  # borders
        text = line[1:-1].strip()
        if not text:
            continue
        if text == "steps:":
            in_steps = True
        elif in_steps:
            name, _, symbol = text.rpartition(":")  # "refinement-tiedbeam:✅"
            groups.setdefault(name.strip(), Counter())[
                SYMBOLS.get(symbol.strip(), "unknown")
            ] += 1
        else:
            key, _, value = text.partition(
                ":"
            )  # split on the first colon only (times contain more)
            fields[key.strip()] = value.strip()

    if "id" not in fields or not groups:
        raise BBFlowError("Couldn't read the pipeline status output.")
    stage = fields.get("current_stage", "")
    return PipelineStatus(
        name=title,
        pipeline_id=fields["id"],
        state=fields.get("status", "unknown").lower(),
        current_stage=int(stage) if stage.isdigit() else None,
        created=_parse_time(fields.get("creation", "")),
        started=_parse_time(fields.get("start", "")),
        groups=groups,
    )
