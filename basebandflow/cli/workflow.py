import typer

import basebandflow.cli.documentation as docs
from basebandflow.api.errors import BBFlowError, InvalidEventId
from basebandflow.api.history import latest_run
from basebandflow.api.workflow import abort, open, parse_pipeline_ps, status
from basebandflow.cli.ui import console, render_pipeline, summary_line

workflow_app = typer.Typer(help="Workflow related commands", no_args_is_help=True)


@workflow_app.command("abort", no_args_is_help=True, help=docs.WORKFLOW_ABORT)
def abort_cmd(config_id: str = typer.Argument("", help=docs.CONFIG_ID)):
    res = abort(config_id)
    if res.returncode != 0:
        raise BBFlowError(f"Couldn't abort Workflow configuration: {config_id}")
    else:
        console.print(f"Successfully terminated configuration: {config_id}")


@workflow_app.command("status", no_args_is_help=True, help=docs.WORKFLOW_STATUS)
def status_cmd(
    event_id: str = typer.Argument("", help=docs.EID),
    oneline: bool = typer.Option(False, help="Oneline status"),
):
    if not event_id:
        raise InvalidEventId()
    last = latest_run(event_id)
    pipeline_id = last.result.pipeline_id
    res = status(pipeline_id)
    if oneline:
        console.print(summary_line(parse_pipeline_ps(res.stdout)))
    else:
        console.print(render_pipeline(parse_pipeline_ps(res.stdout)))


@workflow_app.command("open", help=docs.WORKFLOW_OPEN)
def open_cmd(event_id: str = typer.Argument("", help=docs.EID)):
    last = latest_run(event_id)
    url = open(last.result.config_id)
    console.print("Visit Workflow page:")
    console.print(f"[dim]{url}[/dim]")


def register(app: typer.Typer):
    app.add_typer(workflow_app, name="workflow")
