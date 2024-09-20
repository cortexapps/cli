from datetime import datetime
from enum import Enum
import typer

from rich import print_json

app = typer.Typer()

class Action(str, Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"

class ActorType(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    API_KEY = "API_KEY"
    BACKSTAGE = "BACKSTAGE"
    OAUTH2 = "OAUTH2"
    PERSONAL_API_KEY = "PERSONAL_API_KEY"

class ActorRequestType(str, Enum):
    API_KEY_ENTITY = "API_KEY_ENTITY"
    ATLASSIAN_WEBHOOK = "ATLASSIAN_WEBHOOK"
    SCORECARD_BADGES = "SCORECARD_BADGES"
    SLACK_COMMAND = "SLACK_COMMAND"

# Defined in web/src/main/kotlin/com/brainera/web/audit/models/AuditedEntity.kt
#
# Not sure if we should enumerate this or have user explicitly list the items 
# they want.  User would have to inpsect existing elements to know what the
# possible values are.
#
# Maintenance will be a problem if we use enum.
class ObjectType(str, Enum):
    ACCOUNT_FLAG = "ACCOUNT_FLAG"
    ACTIVE_DIRECTORY_CONFIGURATION = "ACTIVE_DIRECTORY_CONFIGURATION"
    ALLOW_LIST_ENTRY = "ALLOW_LIST_ENTRY"
    API_KEY = "API_KEY"
    ATLASSIAN_CONFIGURATION = "ATLASSIAN_CONFIGURATION"
    AWS_CONFIGURATION = "AWS_CONFIGURATION"
    AZURE_DEVOPS_CONFIGURATION = "AZURE_DEVOPS_CONFIGURATION"
    AZURE_RESOURCES_CONFIGURATION = "AZURE_RESOURCES_CONFIGURATION"
    BAMBOO_HR_CONFIGURATION = "BAMBOO_HR_CONFIGURATION"
    BITBUCKET_CONFIGURATION = "BITBUCKET_CONFIGURATION"
    BITBUCKET_OAUTH_CONFIGURATION = "BITBUCKET_OAUTH_CONFIGURATION"
    BITBUCKET_OAUTH_REGISTRATION = "BITBUCKET_OAUTH_REGISTRATION"
    BITBUCKET_ONPREM_CONFIGURATION = "BITBUCKET_ONPREM_CONFIGURATION"
    BITBUCKET_ONPREM_WEBHOOK_SECRET = "BITBUCKET_ONPREM_WEBHOOK_SECRET"
    BITBUCKET_PERSONAL_CONFIGURATION = "BITBUCKET_PERSONAL_CONFIGURATION"
    BUGSNAG_CONFIGURATION = "BUGSNAG_CONFIGURATION"
    BUILDKITE_CONFIGURATION = "BUILDKITE_CONFIGURATION"
    CATALOG = "CATALOG"
    CATALOG_FILTER = "CATALOG_FILTER"
    CHECKMARX_SAST_CONFIGURATION = "CHECKMARX_SAST_CONFIGURATION"
    CIRCLE_CI_CONFIGURATION = "CIRCLE_CI_CONFIGURATION"
    CLICKUP_CONFIGURATION = "CLICKUP_CONFIGURATION"
    CODECOV_CONFIGURATION = "CODECOV_CONFIGURATION"
    CORALOGIX_CONFIGURATION = "CORALOGIX_CONFIGURATION"
    CORTEX_TEAM_ROLES = "CORTEX_TEAM_ROLES"
    CORTEX_USER = "CORTEX_USER"
    CORTEX_USER_ROLES = "CORTEX_USER_ROLES"
    CUSTOM_DATA = "CUSTOM_DATA"
    CUSTOM_METRICS_CONFIGURATION = "CUSTOM_METRICS_CONFIGURATION"
    CUSTOM_ROLE = "CUSTOM_ROLE"
    DATADOG_CONFIGURATION = "DATADOG_CONFIGURATION"
    DOMAIN = "DOMAIN"
    DYNATRACE_CONFIGURATION = "DYNATRACE_CONFIGURATION"
    ENTITY_TYPE_DEFINITION = "ENTITY_TYPE_DEFINITION"
    ENTITY_VERIFICATION = "ENTITY_VERIFICATION"
    FIREHYDRANT_CONFIGURATION = "FIREHYDRANT_CONFIGURATION"
    GITHUB_APP_CONFIGURATION = "GITHUB_APP_CONFIGURATION"
    GITHUB_APP_INSTALLATION = "GITHUB_APP_INSTALLATION"
    GITHUB_PERSONAL_TOKEN = "GITHUB_PERSONAL_TOKEN"
    GITHUB_WEBHOOK_SECRET = "GITHUB_WEBHOOK_SECRET"
    GITLAB_CONFIGURATION = "GITLAB_CONFIGURATION"
    GOOGLE_CONFIGURATION = "GOOGLE_CONFIGURATION"
    INCIDENT_IO_CONFIGURATION = "INCIDENT_IO_CONFIGURATION"
    INITIATIVE = "INITIATIVE"
    INSTANA_CONFIGURATION = "INSTANA_CONFIGURATION"
    JIRA_BASIC_CONFIGURATION = "JIRA_BASIC_CONFIGURATION"
    JIRA_CONFIGURATION = "JIRA_CONFIGURATION"
    JIRA_OAUTH_CONFIGURATION = "JIRA_OAUTH_CONFIGURATION"
    JIRA_OAUTH_REGISTRATION = "JIRA_OAUTH_REGISTRATION"
    JIRA_ONPREM_CONFIGURATION = "JIRA_ONPREM_CONFIGURATION"
    LAUNCHDARKLY_CONFIGURATION = "LAUNCHDARKLY_CONFIGURATION"
    LIGHTSTEP_CONFIGURATION = "LIGHTSTEP_CONFIGURATION"
    MEND_SAST_CONFIGURATION = "MEND_SAST_CONFIGURATION"
    MEND_SCA_CONFIGURATION = "MEND_SCA_CONFIGURATION"
    MICROSOFT_TEAMS_CONFIGURATION = "MICROSOFT_TEAMS_CONFIGURATION"
    NEWRELIC_CONFIGURATION = "NEWRELIC_CONFIGURATION"
    OAUTH_CONFIGURATION = "OAUTH_CONFIGURATION"
    OKTA_CONFIGURATION = "OKTA_CONFIGURATION"
    OPENAPI_DEFINITION = "OPENAPI_DEFINITION"
    OPSGENIE_CONFIGURATION = "OPSGENIE_CONFIGURATION"
    PAGERDUTY_CONFIGURATION = "PAGERDUTY_CONFIGURATION"
    PERSONAL_API_KEY = "PERSONAL_API_KEY"
    PROMETHEUS_CONFIGURATION = "PROMETHEUS_CONFIGURATION"
    RESOURCE = "RESOURCE"
    ROLLBAR_CONFIGURATION = "ROLLBAR_CONFIGURATION"
    SCORECARD = "SCORECARD"
    SCORECARD_FILTER = "SCORECARD_FILTER"
    SCORECARD_RULE = "SCORECARD_RULE"
    SCORECARD_RULE_FILTER = "SCORECARD_RULE_FILTER"
    SECRET = "SECRET"
    SECRET_GROUP = "SECRET_GROUP"
    SENTRY_CONFIGURATION = "SENTRY_CONFIGURATION"
    SERVICE = "SERVICE"
    SERVICENOW_CONFIGURATION = "SERVICENOW_CONFIGURATION"
    SIGNALFX_CONFIGURATION = "SIGNALFX_CONFIGURATION"
    SLACK_CONFIGURATION = "SLACK_CONFIGURATION"
    SNYK_CONFIGURATION = "SNYK_CONFIGURATION"
    SONARQUBE_CONFIGURATION = "SONARQUBE_CONFIGURATION"
    SUMOLOGIC_CONFIGURATION = "SUMOLOGIC_CONFIGURATION"
    TEAM = "TEAM"
    VERACODE_CONFIGURATION = "VERACODE_CONFIGURATION"
    VERIFICATION_PERIOD = "VERIFICATION_PERIOD"
    VICTOROPS_CONFIGURATION = "VICTOROPS_CONFIGURATION"
    WIZ_CONFIGURATION = "WIZ_CONFIGURATION"
    WORKDAY_CONFIGURATION = "WORKDAY_CONFIGURATION"
    WORKFLOW = "WORKFLOW"
    XMATTERS_CONFIGURATION = "XMATTERS_CONFIGURATION"

@app.command()
def get(
    ctx: typer.Context,
    actions: list[Action] | None = typer.Option(None, "--actions", "-a", help="The audit action"),
    actorApiKeyIdentifiers: list[str] | None = typer.Option(None, "--actorApiKeyIdentifiers", "-ak", help="API key name associated with audit event"),
    actorEmails: list[str] | None = typer.Option(None, "--actorEmails", "-ae", help="Email address associated with audit event"),
    actorIpAddresses: list[str] | None = typer.Option(None, "--actorIpAddresses", "-ai", help="Source IP Addresses associated with audit event"),
    actorRequestTypes: list[ActorRequestType] | None = typer.Option(None, "--actorRequestTypes", "-ar", help="Request event associated with audit event"),
    actorTypes: list[ActorType] | None = typer.Option(None, "--actorTypes", "-at", help="Actor that triggered the audit event"),
    end_time: datetime = typer.Option(None, "--endTime", "-e", help="End time of audit logs to retrieve", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    objectIdentifiers: list[str] | None = typer.Option(None, "--objectIdentifiers", "-oi", help="The name of the Cortex object that was modified, ie x-cortex-tag value, metadata field name, etc."),
    objectTypes: list[ObjectType] | None = typer.Option(None, "--objectTypes", "-ot", help="ObjectTypes"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    start_time: datetime = typer.Option(None, "--startTime", "-s", help="Start time of audit logs to retrieve", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    Note: To see the complete list of possible values, please reference the available filter options for audit logs under Settings in the app.
    """
    client = ctx.obj["client"]

    params = {
        "actions": actions,
        "actorApiKeyIdentifiers": actorApiKeyIdentifiers,
        "actorEmails": actorEmails,
        "actorIpAddresses": actorIpAddresses,
        "actorRequestTypes": actorRequestTypes,
        "actorTypes": actorTypes,
        "endTime": end_time,
        "objectIdentifiers": objectIdentifiers,
        "objectTypes": objectTypes,
        "page": page,
        "pageSize": page_size,
        "startTime": start_time
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    # convert datetime and list types to string
    for k, v in params.items():
        if str(type(v)) == "<class 'datetime.datetime'>":
           params[k] = v.strftime('%Y-%m-%dT%H:%M:%S')
        if str(type(v)) == "<class 'list'>":
            params[k] = ','.join(v)

    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/audit-logs", params=params)
        pass
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/audit-logs", params=params)
        pass

    print_json(data=r)
