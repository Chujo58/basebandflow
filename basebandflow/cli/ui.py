# cli/ui.py (display only, no logic)

# console = Console(): one shared instance, imported everywhere.
# show_banner(status: Status) -> None: prints the login, settings, and token lines.
# print_error(msg: str) -> None: consistent red error formatting.
# print_table(...): a helper for later, used by status. You can skip it for now.

from datetime import datetime

import pandas as pd
from rich.console import Console, Group
from rich.markup import escape
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from basebandflow.models import PipelineStatus, Status, TokenStatus

console = Console()


def show_banner(status: Status) -> None:
    if status.canfar_ok:
        console.print("[green]✔ Logged in to CANFAR[/green]")
    else:
        console.print("[yellow]✖ Not logged in to CANFAR (choose 'Log in')[/yellow]")

    if status.tokens_ok:
        console.print(
            f"[green]✔ Tokens are valid until[/green] [orange]{
                (datetime.now().astimezone() + status.access_token.remaining).strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
            }[/orange]"
        )
    else:
        console.print("[yellow]✖ Tokens are invalid. Run `bbflow tokens refresh`")


def df_to_rich_table(
    df: pd.DataFrame, title: str | None = None, show_index: bool = True
) -> Table:
    """Converts a pandas DataFrame into a rich Table."""
    table = Table(title=title)

    if show_index:
        index_name = str(df.index.name) if df.index.name else ""
        table.add_column(index_name, style="cyan", no_wrap=True)

    for col in df.columns:
        table.add_column(str(col), style="magenta")

    for row_idx, row in df.iterrows():
        row_values = [str(val) for val in row]
        if show_index:
            table.add_row(str(row_idx), *row_values)
        else:
            table.add_row(*row_values)

    return table


def print_table(title: str, data: dict[str, str], show_index: bool = True):
    table = df_to_rich_table(
        pd.DataFrame.from_dict(data), title=title, show_index=show_index
    )
    console.print(table)


def print_error(msg: str) -> None:
    console.print(f"[red]{msg}[/red]")


def canfar_line(status: bool) -> str:
    if status:
        return "[green]✔ CANFAR login is valid.[/green]"
    else:
        return "[yellow]✔ CANFAR login is invalid.[/yellow]"


def token_line(t: TokenStatus) -> str:
    if not t.present:
        return "[red]✖ CHIME/FRB tokens: not found[/red]"
    if t.remaining is None:
        return "[red]✖ CHIME/FRB tokens: unreadable[/red]"
    if t.remaining.total_seconds() <= 0:
        return "[red]✖ CHIME/FRB tokens: expired[/red]"
    mins = int(t.remaining.total_seconds() // 60)
    h, m = divmod(mins, 60)
    left = f"{h}h {m}m" if h else f"{m}m"
    colour = "yellow" if t.needs_refresh else "green"
    return f"[{colour}]✔ CHIME/FRB tokens: valid for {left}[/{colour}]"


STATE_STYLE = {
    "running": "cyan",
    "success": "green",
    "completed": "green",
    "queued": "yellow",
    "failure": "red",
    "failed": "red",
    "cancelled": "red",
}


def _group_symbol(c) -> str:
    total = sum(c.values())
    if c["unknown"]:
        return "[red]?[/red]"
    if c["running"]:
        return "[cyan]▶[/cyan]"
    if c["done"] == total:
        return "[green]✔[/green]"
    if c["done"] or c["queued"]:
        return "[yellow]◔[/yellow]"
    return "[dim]·[/dim]"


def _group_counts(c) -> str:
    total = sum(c.values())
    if total == 1:  # single steps: just the word
        word = next(k for k, v in c.items() if v)
        return {
            "done": "[green]done[/green]",
            "running": "[cyan]running[/cyan]",
            "queued": "[yellow]queued[/yellow]",
            "waiting": "[dim]waiting[/dim]",
            "unknown": "[red]unknown[/red]",
        }[word]
    parts = []
    if c["done"]:
        parts.append(f"[green]{c['done']}/{total} done[/green]")
    if c["running"]:
        parts.append(f"[cyan]{c['running']} running[/cyan]")
    if c["queued"]:
        parts.append(f"[yellow]{c['queued']} queued[/yellow]")
    if c["waiting"] and c["waiting"] != total:
        parts.append(f"[dim]{c['waiting']} waiting[/dim]")
    if c["unknown"]:
        parts.append(f"[red]{c['unknown']} unknown[/red]")
    return "  ".join(parts) if parts else f"[dim]{total} waiting[/dim]"


def render_pipeline(p: PipelineStatus) -> Group:
    colour = STATE_STYLE.get(p.state, "yellow")
    pct = int(100 * p.done / p.total) if p.total else 0

    header = Text.from_markup(
        f"[bold]{escape(p.name)}[/bold]  [{colour}]{escape(p.state)}[/{colour}]"
    )
    meta = []
    if p.current_stage is not None:
        meta.append(f"[dim]stage[/dim] {p.current_stage}")
    if p.started:
        meta.append(f"[dim]started[/dim] {p.started:%b %d, %H:%M}")
    meta.append(f"[dim]id[/dim] [cyan]{escape(p.pipeline_id)}[/cyan]")
    subtitle = Text.from_markup("   ".join(meta))

    bar = Table.grid(padding=(0, 1))
    bar.add_row(
        ProgressBar(
            total=max(p.total, 1),
            completed=p.done,
            width=36,
            complete_style=colour,
            finished_style="green",
        ),
        f"{p.done}/{p.total} steps ({pct}%)",
    )

    rows = Table.grid(padding=(0, 2))
    for name, counts in p.groups.items():
        dim = sum(counts.values()) == counts["waiting"]
        label = f"[dim]{escape(name)}[/dim]" if dim else escape(name)
        rows.add_row(_group_symbol(counts), label, _group_counts(counts))

    parts: list = [header, subtitle, "", bar, "", rows]
    if any(c["unknown"] for c in p.groups.values()):
        parts += [
            "",
            "[red]?[/red] [dim]= a step status this tool doesn't recognize; check `workflow pipelines ps`[/dim]",
        ]
    return Group(*parts)


def summary_line(p: PipelineStatus) -> str:
    """One-liner for `history --live`."""
    if p.state in {"success", "completed"}:
        return "[green]completed[/green]"
    if p.state in {"failure", "failed", "cancelled"}:
        return f"[red]{escape(p.state)}[/red] [dim]({p.done}/{p.total} steps)[/dim]"
    return f"[{STATE_STYLE.get(p.state, 'yellow')}]{p.done}/{p.total} steps, stage {p.current_stage}[/]"
