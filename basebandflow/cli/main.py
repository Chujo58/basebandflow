import questionary
from questionary import Choice

import typer
from rich.console import Console


from basebandflow.cli.login import (
    register_login,
    Status,
    get_status,
    login,
)
from basebandflow.cli.launch import register_launch
from basebandflow.settings import load_settings

app = typer.Typer(
    help="Run the baseband pipeline on CANFAR",
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    # show banner and menu
    with console.status("Checking CANFAR login..."):
        status = get_status()

    show_banner(status)
    menu(ctx)


register_login(app)
register_launch(app, console)


def build_choices(status: Status) -> list[Choice]:
    choices = []
    # put the thing that needs fixing first
    if status.settings is None:
        choices.append(Choice("Set up settings", value="init"))
    if not status.logged_in:
        choices.append(Choice("Log in to CANFAR", value="login"))
    choices += [
        Choice("Launch event(s)", value="launch"),
        Choice("Check job status", value="status"),
        Choice("View logs", value="logs"),
        Choice("Help", value="help"),
        Choice("Quit", value="quit"),
    ]
    return choices


def show_banner(status: Status):
    if status.logged_in:
        console.print("[green]✔ Logged in to CANFAR[/green]")
    else:
        console.print("[yellow]✖ Not logged in to CANFAR (choose 'Log in')[/yellow]")

    if status.settings:
        console.print(f"[green]✔ User:[/green] {status.settings.username}")
    else:
        console.print("[yellow]✖ No username set (choose 'Set up settings')[/yellow]")


def action_launch(ctx):
    raw = questionary.text("Event ID(s), space separated:").ask()
    if raw:
        pass
        # do_launch(raw.split(), dry_run=False)


ACTIONS = {
    # "init": lambda ctx: run_init(),
    "login": lambda ctx: login(),
    "launch": action_launch,
    # "status": lambda ctx: show_status_table(),
    # "logs": action_logs,
    "help": lambda ctx: console.print(ctx.get_help()),
}


def menu(ctx: typer.Context):
    while True:
        status = get_status()
        console.clear()  # optional
        show_banner(status)

        choice = questionary.select(
            "What would you like to do?", choices=build_choices(status)
        ).ask()
        if choice in (None, "quit"):  # None = Ctrl+C / Esc
            break
        ACTIONS[choice](ctx)
        questionary.press_any_key_to_continue().ask()
