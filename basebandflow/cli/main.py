import os
import platform
import sys
from importlib.metadata import version as pkg_version

import typer

import basebandflow.cli.documentation as docs
from basebandflow.api.errors import BBFlowError
from basebandflow.api.status import get_status
from basebandflow.cli import (
    config,
    containers,
    history,
    launch,
    login,
    tokens,
    workflow,
)
from basebandflow.cli.ui import console, print_error, show_banner

app = typer.Typer(
    help="Run the baseband pipeline on CANFAR",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    # show banner and menu
    with console.status("Checking CANFAR login and CHIME/FRB tokens..."):
        status = get_status()

    show_banner(status)
    console.print(ctx.get_help())
    raise typer.Exit()


config.register(app)
containers.register(app)
history.register(app)
launch.register(app)
login.register(app)
tokens.register(app)
workflow.register(app)


@app.command(help=docs.VERSION)
def version():
    console.print(f"[bold cyan]bbflow[/] [bold green]{pkg_version('basebandflow')}[/]")
    console.print(f"[dim]Python[/]   {platform.python_version()}")
    console.print(f"[dim]Platform[/] {platform.system()} {platform.machine()}")


def run() -> None:
    """Real entry point: runs the app, turns BBFlowError into a clean message."""
    try:
        app()
    except BBFlowError as e:
        if os.environ.get("BBFLOW_DEBUG"):
            raise
        print_error(str(e))
        sys.exit(1)
