import typer
from rich.console import Console

from basebandflow.callbacks import get_status
from basebandflow.cli.login import register_login
from basebandflow.cli.launch import register_launch
from basebandflow.cli.menu import show_banner

app = typer.Typer(
    no_args_is_help=True,
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

    show_banner(status, console)
    # run_menu(ctx, console)


register_login(app)
register_launch(app, console)
