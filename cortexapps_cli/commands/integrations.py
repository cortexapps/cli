import json
from rich import print_json
import typer
from typing_extensions import Annotated

import cortexapps_cli.commands.integrations_commands.aws as aws
import cortexapps_cli.commands.integrations_commands.azure_resources as azure_resources
import cortexapps_cli.commands.integrations_commands.azure_devops as azure_devops
import cortexapps_cli.commands.integrations_commands.circleci as circleci
import cortexapps_cli.commands.integrations_commands.coralogix as coralogix
import cortexapps_cli.commands.integrations_commands.datadog as datadog
import cortexapps_cli.commands.integrations_commands.github as github
import cortexapps_cli.commands.integrations_commands.gitlab as gitlab
import cortexapps_cli.commands.integrations_commands.incidentio as incidentio
import cortexapps_cli.commands.integrations_commands.launchdarkly as launchdarkly
import cortexapps_cli.commands.integrations_commands.newrelic as newrelic
import cortexapps_cli.commands.integrations_commands.pagerduty as pagerduty
import cortexapps_cli.commands.integrations_commands.prometheus as prometheus
import cortexapps_cli.commands.integrations_commands.sonarqube as sonarqube

app = typer.Typer(help="Integrations commands", no_args_is_help=True)
app.add_typer(aws.app, name="aws")
app.add_typer(azure_resources.app, name="azure-resources")
app.add_typer(azure_devops.app, name="azure-devops")
app.add_typer(circleci.app, name="circleci")
app.add_typer(coralogix.app, name="coralogix")
app.add_typer(datadog.app, name="datadog")
app.add_typer(github.app, name="github")
app.add_typer(gitlab.app, name="gitlab")
app.add_typer(incidentio.app, name="incidentio")
app.add_typer(launchdarkly.app, name="launchdarkly")
app.add_typer(newrelic.app, name="newrelic")
app.add_typer(pagerduty.app, name="pagerduty")
app.add_typer(prometheus.app, name="prometheus")
app.add_typer(sonarqube.app, name="sonarqube")
