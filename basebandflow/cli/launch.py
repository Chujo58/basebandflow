import typer

from basebandflow.api.auth import refresh_tokens
from basebandflow.api.errors import InvalidTokens, SettingsMissing
from basebandflow.api.launch import launch
from basebandflow.api.models import LaunchResult
from basebandflow.cli.config import run_init
from basebandflow.cli.ui import console

launch_app = typer.Typer(help="Launch the baseband-pipeline")


def summarize(result: LaunchResult, dry_run: bool):
    # Print a few things to the user so that they know what got launched.
    console.print(f"Information from launch for event ID {result.event_id}")
    console.print(f"Configuration stored in {result.config_path}")
    if dry_run:
        return
    console.print(
        f"[green]✔ Workflow launched:[/green] [bold]{result.pipeline_name}[/bold]\n"
        f"  [dim]Pipeline ID:[/dim] [cyan]{result.pipeline_id}[/cyan]\n"
        f"  [dim]Config ID:  [/dim] [cyan]{result.config_id}[/cyan]"
    )


@launch_app.command("launch")
def launch_cmd(event_id: str, dry_run: bool = typer.Option(False, "--dry-run")):
    """Launch the baseband pipeline"""
    for attempt in range(3):  # bounded, so it can never loop forever
        try:
            result = launch(event_id, dry_run=dry_run)
            break
        except SettingsMissing:
            if not typer.confirm("No username set. Set it now?", default=True):
                raise typer.Exit(1)
            run_init()
        except InvalidTokens:
            console.print(
                "[yellow]CHIME/FRB tokens need refreshing. You'll be asked for your password.[/yellow]"
            )
            refresh_tokens()
        # NotLoggedIn / anything else: not caught here, so it reaches the global handler in run()
    else:
        raise typer.Exit(1)

    summarize(result, dry_run)


def register(app: typer.Typer):
    app.add_typer(launch_app)
