import typer
import rich

from basebandflow.settings import load_settings

from .login import is_logged_in


# Register the commands
def register_launch(app: typer.Typer, console: rich.console.Console):
    @app.command()
    def launch(
        event_ids: list[str] = typer.Argument(..., help="One or more event IDs"),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Render and validate only"
        ),
    ):
        settings = load_settings()
        if settings is None:
            if typer.confirm("No username set. Set it now?", default=True):
                pass
                # settings = run_init()  # same function `config init` calls
            else:
                raise typer.Exit(1)

        if not dry_run and not is_logged_in():
            console.print(
                "[red]Not logged in to CANFAR. Run `bbflow login` first.[/red]"
            )
            raise typer.Exit(1)
