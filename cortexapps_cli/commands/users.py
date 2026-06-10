import typer
import cortexapps_cli.commands.users_commands.roles as roles

app = typer.Typer(help="Users commands", no_args_is_help=True)
app.add_typer(roles.app, name="roles")
