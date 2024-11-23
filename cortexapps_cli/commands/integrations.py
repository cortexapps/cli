import json
from rich import print_json
import typer
from typing_extensions import Annotated

import cortexapps_cli.commands.integrations_commands.aws as aws

app = typer.Typer(help="Integrations commands",
                  no_args_is_help=True)
app.add_typer(aws.app, name="aws")
