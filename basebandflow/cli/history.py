import typer
from rich.markup import escape
from rich.table import Table

from basebandflow.api.history import RunRecord, latest_run, list_runs
from basebandflow.cli.ui import console

history_app = typer.Typer(help="Past launches", invoke_without_command=True)

_STATUS_STYLE = {
    "running": "green",
    "completed": "green",
    "deployed": "yellow",  # deployed but workers never started
    "failed": "red",
    "rendered": "dim",  # dry run
}


def _when(rec: RunRecord) -> str:
    return rec.started.strftime("%Y-%m-%d %H:%M") if rec.started else "?"


@history_app.callback()
def history(
    ctx: typer.Context,
    event: str | None = typer.Option(None, "--event", "-e", help="Only this event ID"),
    limit: int = typer.Option(10, "--limit", "-n", min=1, help="How many runs to show"),
    all_: bool = typer.Option(False, "--all", "-a", help="Include dry runs"),
):
    """List recent launches, newest first."""
    if ctx.invoked_subcommand is not None:
        return

    runs = list_runs(event, limit=limit, include_dry_runs=all_)
    if not runs:
        console.print("[yellow]No launches found.[/yellow]")
        raise typer.Exit()

    table = Table(show_edge=False, header_style="dim")
    table.add_column("When")
    table.add_column("Event", style="cyan")
    table.add_column("Status (at launch)")
    table.add_column("Workers", justify="right")
    table.add_column("Config ID")
    table.add_column("Pipeline ID", style="cyan")

    for rec in runs:
        r = rec.result
        if r is None:
            table.add_row(
                _when(rec), escape(rec.event_id), "[red]unreadable[/red]", "-", "-"
            )
            continue
        style = _STATUS_STYLE.get(r.status, "white")
        table.add_row(
            _when(rec),
            escape(rec.event_id),
            f"[{style}]{escape(r.status)}[/{style}]",
            str(len(r.containers)),
            escape(r.config_id or "-"),
            escape(r.pipeline_id or "-"),
        )
    console.print(table)


@history_app.command("show")
def show(
    event_id: str = typer.Argument(..., help="Event ID (shows its most recent launch)"),
):
    """Details of the most recent launch for an event."""
    rec = latest_run(event_id)
    if rec is None:
        console.print(f"[yellow]No launches found for {escape(event_id)}.[/yellow]")
        raise typer.Exit(1)
    if rec.result is None:
        console.print(f"[red]Record at {escape(str(rec.path))} is unreadable.[/red]")
        raise typer.Exit(1)

    r = rec.result
    console.print(
        f"[bold]{escape(r.pipeline_name or '')}[/bold]  [dim]{_when(rec)}[/dim]"
    )
    for label, value in [
        ("Status", r.status),
        ("Pipeline ID", r.pipeline_id or "-"),
        ("Config ID", r.config_id or "-"),
        ("Config file", r.config_path),
        ("Run folder", str(rec.path)),
    ]:
        console.print(f"  [dim]{label + ':':<12}[/dim] [cyan]{escape(value)}[/cyan]")
    for c in r.containers:
        console.print(
            f"  [dim]worker:[/dim] {escape(str(c.model_dump()))}"
        )  # adjust to your Container fields


def register(app: typer.Typer):
    app.add_typer(history_app, name="history")
