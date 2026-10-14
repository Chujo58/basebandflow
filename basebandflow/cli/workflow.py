import typer

from basebandflow.api.errors import BBFlowError, InvalidEventId
from basebandflow.api.history import latest_run
from basebandflow.api.workflow import abort, parse_pipeline_ps, status
from basebandflow.cli.ui import console, render_pipeline, summary_line

workflow_app = typer.Typer(help="Workflow related commands")


@workflow_app.command("abort", no_args_is_help=True)
def abort_cmd(config_id: str = typer.Argument("", help="Config ID for Workflow")):
    """Abort Workflow deployment"""
    res = abort(config_id)
    if res.returncode != 0:
        raise BBFlowError(f"Couldn't abort Workflow configuration: {config_id}")
    else:
        console.print(f"Successfully terminated configuration: {config_id}")


@workflow_app.command("status", no_args_is_help=True)
def status_cmd(
    event_id: str = typer.Argument("", help="Event ID of the baseband pipeline run"),
    oneline: bool = typer.Option(False, help="Oneline status"),
):
    """Check status of baseband pipeline"""
    if not event_id:
        raise InvalidEventId()
    last = latest_run(event_id)
    pipeline_id = last.result.pipeline_id
    res = status(pipeline_id)
    if oneline:
        console.print(summary_line(parse_pipeline_ps(res.stdout)))
    else:
        console.print(render_pipeline(parse_pipeline_ps(res.stdout)))


def register(app: typer.Typer):
    app.add_typer(workflow_app)
