# cli/ui.py (display only, no logic)

# console = Console(): one shared instance, imported everywhere.
# show_banner(status: Status) -> None: prints the login, settings, and token lines.
# print_error(msg: str) -> None: consistent red error formatting.
# print_table(...): a helper for later, used by status. You can skip it for now.

from datetime import datetime

import pandas as pd
from rich.console import Console
from rich.table import Table

from basebandflow.api.models import Status, TokenStatus

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


def print_table(title: str, data: dict[str, str]):
    table = df_to_rich_table(pd.DataFrame.from_dict(data), title=title)
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
