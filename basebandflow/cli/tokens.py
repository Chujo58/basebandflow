import typer

import basebandflow.cli.documentation as docs
from basebandflow.api.auth import check_tokens
from basebandflow.api.auth.tokens import TOKEN_FILE, refresh_tokens
from basebandflow.cli.ui import console, token_line

tokens_app = typer.Typer(help=docs.TOKENS_TYPER, invoke_without_command=True)


def show_token_status():
    access, _ = check_tokens()
    console.print(token_line(access))


@tokens_app.callback()
def tokens(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        show_token_status()
        console.print(ctx.get_help())


@tokens_app.command(help=docs.TOKEN_PATH)
def path():
    console.print(f"Tokens are saved at: {TOKEN_FILE}")


@tokens_app.command("status", help=docs.TOKEN_STATUS)
def token_status():
    show_token_status()


@tokens_app.command("refresh", help=docs.TOKEN_REFRESH)
def refresh_cmd():
    console.print("You'll be asked for your CHIME/FRB password.")
    refresh_tokens()  # no console.status spinner around this
    show_token_status()


def register(app: typer.Typer):
    app.add_typer(tokens_app, name="tokens")
