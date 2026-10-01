import typer

from basebandflow.callbacks import login


# Register the commands
def register_login(app: typer.Typer):
    @app.command(
        name="login",
        help="Wrapper for login to CANFAR Science Platform.",
        rich_help_panel="Login",
    )
    def login_command():
        login()
