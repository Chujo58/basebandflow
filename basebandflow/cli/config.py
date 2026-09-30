import typer
from importlib.resources import files
from jinja2 import Environment, StrictUndefined
import yaml


def render_config(context: dict) -> tuple[str, dict]:
    text = (files("basebandflow") / "templates" / "pipeline_config.yaml.j2").read_text()
    env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    rendered = env.from_string(text).render(**context)
    parsed = yaml.safe_load(rendered)
    return rendered, parsed

