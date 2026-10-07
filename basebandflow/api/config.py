from importlib.resources import files
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined

from basebandflow.api.errors import (
    ConfigRenderError,
    TemplateError,
)
from basebandflow.api.models import RenderedConfig
from basebandflow.api.validate import validate_event_id, validate_username

MATRIX_EXPR = "${{ matrix.job_id }}"


def load_template() -> str:  # importlib.resources
    return (files("basebandflow") / "templates" / "pipeline_config.yaml.j2").read_text()


def render_config(username: str, event_id: str, directory: Path) -> RenderedConfig:
    username = validate_username(username)
    event_id = validate_event_id(event_id)

    env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    try:
        text = env.from_string(load_template()).render(
            username=username, event_id=event_id
        )
        parsed = yaml.safe_load(text)
    except (TemplateError, yaml.YAMLError) as e:
        raise ConfigRenderError(f"Could not render config: {e}") from e

    _check_rendered(parsed, event_id)

    path = directory / "config.yaml"
    path.write_text(
        text, encoding="utf-8"
    )  # exact rendered text: anchors and comments intact
    return RenderedConfig(text=text, parsed=parsed, path=path, event_id=event_id)


def _check_rendered(parsed, event_id: str) -> None:
    """Sanity checks on the rendered result. Raises ConfigRenderError."""
    if not isinstance(parsed, dict):
        raise ConfigRenderError("Rendered config is not a YAML mapping.")
    if (
        str(parsed.get("event_number")) != event_id
        or parsed.get("event_str") != event_id
    ):
        raise ConfigRenderError("Event ID did not render correctly.")

    for step in parsed.get("pipeline", {}).get("steps", []):
        if "matrix" in step:  # workflow expression must survive rendering untouched
            job_id = step.get("work", {}).get("parameters", {}).get("job_id")
            if job_id != MATRIX_EXPR:
                raise ConfigRenderError(
                    f"Step {step.get('name')!r}: matrix expression was altered."
                )
