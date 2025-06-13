from collections import defaultdict
from datetime import datetime
from enum import Enum
import json
from rich import print_json
import typer
from typing_extensions import Annotated

class DiscoveryType(str, Enum):
    APM_RESOURCE_NOT_DETECTED = "APM_RESOURCE_NOT_DETECTED"
    AWS_RESOURCE_NOT_DETECTED = "AWS_RESOURCE_NOT_DETECTED"
    AZURE_RESOURCE_NOT_DETECTED = "AZURE_RESOURCE_NOT_DETECTED"
    ECS_RESOURCE_NOT_DETECTED = "ECS_RESOURCE_NOT_DETECTED"
    GOOGLE_CLOUD_RESOURCE_NOT_DETECTED = "GOOGLE_CLOUD_RESOURCE_NOT_DETECTED"
    NEW_APM_RESOURCE = "NEW_APM_RESOURCE"
    NEW_AWS_RESOURCE = "NEW_AWS_RESOURCE"
    NEW_AZURE_RESOURCE = "NEW_AZURE_RESOURCE"
    NEW_ECS_RESOURCE = "NEW_ECS_RESOURCE"
    NEW_GOOGLE_CLOUD_RESOURCE = "NEW_GOOGLE_CLOUD_RESOURCE"
    NEW_K8S_RESOURCE = "NEW_K8S_RESOURCE"
    NEW_REPOSITORY = "NEW_REPOSITORY"
    REPOSITORY_ARCHIVED = "REPOSITORY_ARCHIVED"
    REPOSITORY_DELETED = "REPOSITORY_DELETED"

class DiscoverySource(str, Enum):
    AWS = "AWS"
    AZURE_DEVOPS = "AZURE_DEVOPS"
    AZURE_RESOURCES = "AZURE_RESOURCES"
    BITBUCKET = "BITBUCKET"
    DATADOG = "DATADOG"
    DYNATRACE = "DYNATRACE"
    ECS = "ECS"
    GCP = "GCP"
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    INSTANA = "INSTANA"
    K8S = "K8S"
    LIGHTSTEP = "LIGHTSTEP"
    LAMBDA = "LAMBDA"
    LAMBDA_CLOUD_CONTROL = "LAMBDA_CLOUD_CONTROL"
    NEWRELIC = "NEWRELIC"
    SERVICENOW = "SERVICENOW"
    SERVICENOW_DOMAIN = "SERVICENOW_DOMAIN"

app = typer.Typer(help="Discovery Audit commands", no_args_is_help=True)

@app.command()
def get(
    ctx: typer.Context,
    include_ignored: bool = typer.Option(False, "--include-ignored", "-ii", help="Include ignore events in result"),
    type: DiscoveryType = typer.Option(None, "--type", "-ty", help="The type of audit event"),
    source: DiscoverySource = typer.Option(None, "--source", "-s", help="The source of the audit event"),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
):
    """
    This report shows you recent changes in your environment that aren't reflected in Cortex, including newly created repositories, services, and resources that we discover from your integrations or which were deleted in the environment but corresponding Cortex entities are still present.
    """

    client = ctx.obj["client"]

    params = {
       "includeIgnored": include_ignored,
       "page": page,
       "pageSize": page_size,
       "source": source,
       "type": type
    }       

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}
    
    if page is None:
        # if page is not specified, we want to fetch all pages
        r = client.fetch("api/v1/discovery-audit", params=params)
    else:
        # if page is specified, we want to fetch only that page
        r = client.get("api/v1/discovery-audit", params=params)

    print_json(data=r)
