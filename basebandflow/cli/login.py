import typer

import basebandflow.cli.documentation as docs
from basebandflow.api.auth.canfar import is_logged_in, login_interactive
from basebandflow.cli.ui import canfar_line, console

login_app = typer.Typer(help=docs.LOGIN_TYPER)


@login_app.command(help=docs.LOGIN_LOGIN)
def login(check: bool = typer.Option(False, "--check", help=docs.LOGIN_CHECK)):
    if check:
        ok = is_logged_in()
        console.print(canfar_line(ok))
        raise typer.Exit(0 if ok else 1)

    if is_logged_in():
        console.print("[green]✔ Already logged in to CANFAR[/green]")
        return
    login_interactive()  # inherits the terminal
    ok = is_logged_in()
    console.print(canfar_line(ok))
    raise typer.Exit(0 if ok else 1)


def register(app: typer.Typer):
    app.add_typer(login_app)
