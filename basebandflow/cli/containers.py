import typer
from rich.table import Table

import basebandflow.cli.documentation as docs
from basebandflow.api.auth import refresh_and_verify
from basebandflow.api.containers import *
from basebandflow.api.errors import InvalidTokens, SettingsMissing
from basebandflow.cli.config import run_init
from basebandflow.cli.ui import console

container_app = typer.Typer(
    help=docs.CONTAINERS_TYPER,
    no_args_is_help=True,
)

STATUS_STYLES = {
    "pending": "yellow",
    "running": "bold green",
    "terminating": "magenta",
    "succeeded": "green",
    "completed": "green",
    "error": "bold red",
    "failed": "bold red",
}


def style_status(status: str) -> str:
    style = STATUS_STYLES.get(str(status).lower(), "dim")
    return f"[{style}]{status}[/{style}]"


def filter_complete():
    return "datatrail", "analysis", "refinement"


@container_app.command("create", no_args_is_help=True, help=docs.CONTAINER_CREATE)
def create(
    session_type: str = typer.Argument(
        None,
        help=f"Type of session: {', '.join(filter_complete())}",
    ),
):
    if not session_type or session_type not in filter_complete():
        console.print(f"Invalid session type selected: [red]{session_type}[/red]")
        console.print(f"Please select from: [dim]{', '.join(filter_complete())}[/dim]")
        typer.Exit(1)

    try:
        initialize_session_container(session_type)
    except SettingsMissing:
        if not typer.confirm("No username set. Set it now?", default=True):
            raise typer.Exit(1)
        run_init()
    except InvalidTokens:
        console.print(
            "[yellow]CHIME/FRB tokens need refreshing. You'll be asked for your password.[/yellow]"
        )
        refresh_and_verify()


@container_app.command("list", help=docs.CONTAINER_LIST)
def list_cmd(
    filtering: str = typer.Option(
        None, "--filter", "-f", autocompletion=filter_complete
    ),
):
    containers = list_headless_containers()
    if filtering:
        containers = [c for c in containers if c.type == filtering]

    table = Table(
        title="CANFAR headless sessions",
        header_style="bold cyan",
        row_styles=["", "dim"],  # subtle zebra striping
        show_lines=False,
    )
    table.add_column("Session IDs", style="bright_blue", no_wrap=True)
    table.add_column("Session Names", style="white")
    table.add_column("Status")
    if not filtering:
        table.add_column("Type", style="cyan")

    for cont in containers:
        row = [cont.session_id, cont.session_name, style_status(cont.status)]
        if not filtering:
            row.append(str(cont.type))
        table.add_row(*row)

    console.print(table)

    # one-line summary, e.g. "5 running, 2 pending"
    counts = {}
    for cont in containers:
        key = str(cont.status).lower()
        counts[key] = counts.get(key, 0) + 1
    if counts:
        console.print(
            ", ".join(
                f"[{STATUS_STYLES.get(k, 'dim')}]{v} {k}[/]" for k, v in counts.items()
            )
        )


@container_app.command("delete", no_args_is_help=True, help=docs.CONTAINER_DELETE)
def delete(
    session_id: str = typer.Argument(help="CANFAR session ID"),
):
    if not session_id:
        console.print(f"Invalid session ID: {session_id}")
        typer.Exit(1)

    res = delete_container(session_id)
    if res:
        console.print("Session deletion successful.")
    else:
        console.print("Session deletion unsuccessful.")


@container_app.command("prune", no_args_is_help=True, help=docs.CONTAINER_PRUNE)
def prune(
    session_type: str = typer.Argument(
        None,
        help=f"Type of session: {', '.join(filter_complete())}",
    ),
):
    if not session_type or session_type not in filter_complete():
        console.print(f"Invalid session type selected: [red]{session_type}[/red]")
        console.print(f"Please select from: [dim]{', '.join(filter_complete())}[/dim]")
        typer.Exit(1)

    res = prune_containers(session_type)
    if res:
        console.print("Session deletion successful.")
    else:
        console.print("Session deletion unsuccessful.")


def register(app: typer.Typer):
    app.add_typer(container_app, name="containers")
