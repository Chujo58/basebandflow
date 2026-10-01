import typer
import rich

from basebandflow.callbacks import validate_launch


# Register the commands
def register_launch(app: typer.Typer, console: rich.console.Console):
    @app.command()
    def launch(
        event_ids: list[str] = typer.Argument(..., help="One or more event IDs"),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Render and validate only"
        ),
    ):
        try:
            validate_launch(dry_run)
        except RuntimeError as error:
            if typer.confirm(str(error) + " Set it now?", default=True):
                pass
            else:
                raise typer.Exit(1)
        except PermissionError as error:
            console.print(f"[red]{error}[/red]")
            raise typer.Exit(1)
