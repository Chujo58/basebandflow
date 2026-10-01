import questionary
from questionary import Choice
from rich.console import Console

from basebandflow.callbacks import Status, get_status, login


def build_choices(status: Status) -> list[Choice]:
    choices = []
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


def show_banner(status: Status, console: Console) -> None:
    if status.logged_in:
        console.print("[green]✔ Logged in to CANFAR[/green]")
    else:
        console.print("[yellow]✖ Not logged in to CANFAR (choose 'Log in')[/yellow]")

    if status.settings:
        console.print(f"[green]✔ User:[/green] {status.settings.username}")
    else:
        console.print("[yellow]✖ No username set (choose 'Set up settings')[/yellow]")


def run_menu(ctx, console: Console) -> None:
    while True:
        status = get_status()
        console.clear()
        show_banner(status, console)

        choice = questionary.select(
            "What would you like to do?", choices=build_choices(status)
        ).ask()
        if choice in (None, "quit"):
            break
        if choice == "login":
            login()
        elif choice == "help":
            console.print(ctx.get_help())
        questionary.press_any_key_to_continue().ask()
