import typer
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from basebandflow.api.auth import refresh_and_verify
from basebandflow.api.errors import InvalidTokens, SettingsMissing
from basebandflow.api.launch import launch, step_count
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


def _run_with_progress(event_id: str, dry_run: bool) -> LaunchResult:
    total = step_count(dry_run)
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(bar_width=20),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Starting", total=total)
        started = 0

        def on_step(label: str) -> None:
            nonlocal started
            progress.update(
                task, completed=started, description=label
            )  # previous steps are done
            started += 1

        result = launch(event_id, dry_run=dry_run, on_step=on_step)
        progress.update(task, completed=total, description="[green]Done[/green]")
    return result


@launch_app.command("launch")
def launch_cmd(event_id: str, dry_run: bool = typer.Option(False, "--dry-run")):
    """Launch the baseband pipeline"""
    for attempt in range(3):  # bounded, so it can never loop forever
        try:
            result = _run_with_progress(event_id, dry_run)
            break
        except SettingsMissing:
            if not typer.confirm("No username set. Set it now?", default=True):
                raise typer.Exit(1)
            run_init()
        except InvalidTokens:
            console.print(
                "[yellow]CHIME/FRB tokens need refreshing. You'll be asked for your password.[/yellow]"
            )
            refresh_and_verify()
        # NotLoggedIn / anything else: not caught here, so it reaches the global handler in run()
    else:
        raise typer.Exit(1)

    summarize(result, dry_run)


def register(app: typer.Typer):
    app.add_typer(launch_app)
