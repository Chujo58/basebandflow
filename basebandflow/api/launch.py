from collections.abc import Callable
from pathlib import Path
from typing import Literal

import yaml

from basebandflow.api.auth import ensure_ready_for_launch
from basebandflow.api.auth.tokens import load_tokens
from basebandflow.api.config import render_config
from basebandflow.api.containers import *
from basebandflow.api.settings import require_settings, run_dir
from basebandflow.api.validate import validate_event_id
from basebandflow.api.workflow import deploy
from basebandflow.models import Container, LaunchResult, RenderedConfig

StepCallback = Callable[[str], None]


def step_count(dry_run: bool) -> int:
    """How many steps launch() will announce. Keep in sync with the step() calls below."""
    return 4 if dry_run else 8


def save_launch_result(result: LaunchResult, directory: Path):
    launch_result_file = directory / "launch_results.yaml"
    tmp = launch_result_file.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(result.model_dump(mode="json")))
    tmp.replace(launch_result_file)


def launch(
    event_id: str, *, dry_run: bool, on_step: StepCallback | None = None
) -> LaunchResult:
    def step(label: str) -> None:
        if on_step:
            on_step(label)

    # 1. Settings check:
    step("Loading bbflow settings...")
    settings = require_settings()

    # 2. Validate event_id
    step("Validating event ID...")
    event_id = validate_event_id(event_id)

    # 3. Create the run directory:
    step("Creating run directory...")
    directory = run_dir(event_id)

    # 4. Render config:
    step("Rendering configuration...")
    configuration = render_config(settings.username, event_id, directory)
    # If dry run, we stop here and save the launch result.
    if dry_run:
        result = generate_launch_record(event_id, "rendered", directory, configuration)
        return result

    # 5. Check ready for launch: CANFAR logged in, and tokens that are valid.
    step("Checking authentication...")
    ensure_ready_for_launch()
    access, refresh = load_tokens()

    # 6. Submit job
    step("Deployment of baseband-analysis...")
    _, config_id, pipeline_id = deploy(str(configuration.path))
    result = generate_launch_record(
        event_id,
        "deployed",
        directory,
        configuration,
        pipeline_id[0],
        config_id,
        containers=[],
    )

    # 7. Launch the containers!!!!!!!!!
    step("Launching containers...")
    containers = []

    skip_datatrail, skip_analysis, skip_refinement = skip_container_creation()

    # 7a. Datatrail
    if not skip_datatrail:
        datatrail_containers = spawn_datatrail_container(settings)
        containers.extend(datatrail_containers)

    # 7b. Analysis
    if not skip_analysis:
        analysis_containers = spawn_analysis_container(settings, access, refresh)
        containers.extend(analysis_containers)

    # 7c. Refinement
    if not skip_refinement:
        refinement_containers = spawn_refinement_container(settings, access, refresh)
        containers.extend(refinement_containers)

    step("Saving launch record...")
    # 8. Save the launch result:
    result = generate_launch_record(
        event_id,
        "running",
        directory,
        configuration,
        pipeline_id[0],
        config_id,
        containers=containers,
    )
    return result


def count_existing_containers(existing_containers: list[Container]):
    datatrail_count = 0
    analysis_count = 0
    refinement_count = 0
    for container in existing_containers:
        if container.type == "datatrail":
            datatrail_count += 1
        if container.type == "analysis":
            analysis_count += 1
        if container.type == "refinement":
            refinement_count += 1

    return datatrail_count, analysis_count, refinement_count


def skip_container_creation():
    existing_containers = list_headless_containers()
    dtc, anc, rfc = count_existing_containers(existing_containers)
    return dtc == 2, anc == 10, rfc == 1


def generate_launch_record(
    event_id: str,
    status: Literal["deployed", "rendered", "running", "failed", "completed"],
    directory: Path,
    configuration: RenderedConfig,
    pipeline_id: str = "",
    config_id: str = "",
    containers: list[Container] | None = None,
):
    if containers is None:
        containers = []

    result = LaunchResult(
        event_id=event_id,
        status=status,
        config_path=str(configuration.path),
        pipeline_id=pipeline_id,
        pipeline_name=configuration.parsed.get("name"),
        config_id=config_id,
        containers=containers,
    )
    save_launch_result(result, directory)
    return result
