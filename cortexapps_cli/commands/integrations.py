import json
from rich import print_json
import typer
from typing_extensions import Annotated

import cortexapps_cli.commands.integrations_commands.aws as aws
import cortexapps_cli.commands.integrations_commands.azure_resources as azure_resources
import cortexapps_cli.commands.integrations_commands.azure_devops as azure_devops
import cortexapps_cli.commands.integrations_commands.circleci as circleci

app = typer.Typer(help="Integrations commands",
                  no_args_is_help=True)
app.add_typer(aws.app, name="aws")
app.add_typer(azure_resources.app, name="azure-resources")
app.add_typer(azure_devops.app, name="azure-devops")
app.add_typer(circleci.app, name="circleci")
