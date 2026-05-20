import json
from rich import print_json
import typer
from typing_extensions import Annotated

import cortexapps_cli.commands.integrations_commands.apiiro as apiiro
import cortexapps_cli.commands.integrations_commands.argocd as argocd
import cortexapps_cli.commands.integrations_commands.aws as aws
import cortexapps_cli.commands.integrations_commands.azure_active_directory as azure_active_directory
import cortexapps_cli.commands.integrations_commands.azure_resources as azure_resources
import cortexapps_cli.commands.integrations_commands.azure_devops as azure_devops
import cortexapps_cli.commands.integrations_commands.bamboohr as bamboohr
import cortexapps_cli.commands.integrations_commands.bitbucket as bitbucket
import cortexapps_cli.commands.integrations_commands.bugsnag as bugsnag
import cortexapps_cli.commands.integrations_commands.buildkite as buildkite
import cortexapps_cli.commands.integrations_commands.checkmarx_sast as checkmarx_sast
import cortexapps_cli.commands.integrations_commands.circleci as circleci
import cortexapps_cli.commands.integrations_commands.clickup as clickup
import cortexapps_cli.commands.integrations_commands.codecov as codecov
import cortexapps_cli.commands.integrations_commands.coralogix as coralogix
import cortexapps_cli.commands.integrations_commands.datadog as datadog
import cortexapps_cli.commands.integrations_commands.dynatrace as dynatrace
import cortexapps_cli.commands.integrations_commands.firehydrant as firehydrant
import cortexapps_cli.commands.integrations_commands.github as github
import cortexapps_cli.commands.integrations_commands.gitlab as gitlab
import cortexapps_cli.commands.integrations_commands.incidentio as incidentio
import cortexapps_cli.commands.integrations_commands.instana as instana
import cortexapps_cli.commands.integrations_commands.jenkins as jenkins
import cortexapps_cli.commands.integrations_commands.jira as jira
import cortexapps_cli.commands.integrations_commands.launchdarkly as launchdarkly
import cortexapps_cli.commands.integrations_commands.mend_sast as mend_sast
import cortexapps_cli.commands.integrations_commands.mend_sca as mend_sca
import cortexapps_cli.commands.integrations_commands.newrelic as newrelic
import cortexapps_cli.commands.integrations_commands.okta as okta
import cortexapps_cli.commands.integrations_commands.opsgenie as opsgenie
import cortexapps_cli.commands.integrations_commands.pagerduty as pagerduty
import cortexapps_cli.commands.integrations_commands.prometheus as prometheus
import cortexapps_cli.commands.integrations_commands.rollbar as rollbar
import cortexapps_cli.commands.integrations_commands.rootly as rootly
import cortexapps_cli.commands.integrations_commands.semgrep as semgrep
import cortexapps_cli.commands.integrations_commands.sentry as sentry
import cortexapps_cli.commands.integrations_commands.servicenow as servicenow
import cortexapps_cli.commands.integrations_commands.servicenow_cloud_observability as servicenow_cloud_observability
import cortexapps_cli.commands.integrations_commands.snyk as snyk
import cortexapps_cli.commands.integrations_commands.sonarqube as sonarqube
import cortexapps_cli.commands.integrations_commands.splunk_observability_cloud as splunk_observability_cloud
import cortexapps_cli.commands.integrations_commands.splunk_on_call as splunk_on_call
import cortexapps_cli.commands.integrations_commands.sumologic as sumologic
import cortexapps_cli.commands.integrations_commands.veracode as veracode
import cortexapps_cli.commands.integrations_commands.wiz as wiz
import cortexapps_cli.commands.integrations_commands.workday as workday
import cortexapps_cli.commands.integrations_commands.xmatters as xmatters

app = typer.Typer(help="Integrations commands", no_args_is_help=True)
app.add_typer(apiiro.app, name="apiiro")
app.add_typer(argocd.app, name="argocd")
app.add_typer(aws.app, name="aws")
app.add_typer(azure_active_directory.app, name="azure-active-directory")
app.add_typer(azure_resources.app, name="azure-resources")
app.add_typer(azure_devops.app, name="azure-devops")
app.add_typer(bamboohr.app, name="bamboohr")
app.add_typer(bitbucket.app, name="bitbucket")
app.add_typer(bugsnag.app, name="bugsnag")
app.add_typer(buildkite.app, name="buildkite")
app.add_typer(checkmarx_sast.app, name="checkmarx-sast")
app.add_typer(circleci.app, name="circleci")
app.add_typer(clickup.app, name="clickup")
app.add_typer(codecov.app, name="codecov")
app.add_typer(coralogix.app, name="coralogix")
app.add_typer(datadog.app, name="datadog")
app.add_typer(dynatrace.app, name="dynatrace")
app.add_typer(firehydrant.app, name="firehydrant")
app.add_typer(github.app, name="github")
app.add_typer(gitlab.app, name="gitlab")
app.add_typer(incidentio.app, name="incidentio")
app.add_typer(instana.app, name="instana")
app.add_typer(jenkins.app, name="jenkins")
app.add_typer(jira.app, name="jira")
app.add_typer(launchdarkly.app, name="launchdarkly")
app.add_typer(mend_sast.app, name="mend-sast")
app.add_typer(mend_sca.app, name="mend-sca")
app.add_typer(newrelic.app, name="newrelic")
app.add_typer(okta.app, name="okta")
app.add_typer(opsgenie.app, name="opsgenie")
app.add_typer(pagerduty.app, name="pagerduty")
app.add_typer(prometheus.app, name="prometheus")
app.add_typer(rollbar.app, name="rollbar")
app.add_typer(rootly.app, name="rootly")
app.add_typer(semgrep.app, name="semgrep")
app.add_typer(sentry.app, name="sentry")
app.add_typer(servicenow.app, name="servicenow")
app.add_typer(servicenow_cloud_observability.app, name="servicenow-cloud-observability")
app.add_typer(snyk.app, name="snyk")
app.add_typer(sonarqube.app, name="sonarqube")
app.add_typer(splunk_observability_cloud.app, name="splunk-observability-cloud")
app.add_typer(splunk_on_call.app, name="splunk-on-call")
app.add_typer(sumologic.app, name="sumo-logic")
app.add_typer(veracode.app, name="veracode")
app.add_typer(wiz.app, name="wiz")
app.add_typer(workday.app, name="workday")
app.add_typer(xmatters.app, name="xmatters")
