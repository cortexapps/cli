from collections import defaultdict
from datetime import datetime
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Custom metrics commands")

# Need a helper function to parse custom_data.
# cannot do this in type: list[Tuple[str, str]] | None  = typer.Option(None)
# Results in: 
# AssertionError: List types with complex sub-types are not currently supported
#
# borrowed from https://github.com/fastapi/typer/issues/387
def _parse_key_value(values):
    if values is None:
        return []
    result = []
    for value in values:
        ts, v = value.split('=')
        result.append({"timestamp": ts, "value": v})
    return result

def _convert_datetime_to_string(params):
    for k, v in params.items():
        if str(type(v)) == "<class 'datetime.datetime'>":
           params[k] = v.strftime('%Y-%m-%dT%H:%M:%S')
    return params

@app.command()
def get(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    custom_metric_key: str = typer.Option(..., "--custom-metric-key", "-k", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    start_date: datetime = typer.Option(None, "--start-date", "-s", help="Start date for the filter (inclusive). Default: 6 months", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    end_date: datetime = typer.Option(None, "--end-date", "-s", help="End date for the filter (inclusive)", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    page: int | None = typer.Option(None, "--page", "-p", help="Page number to return, 0 indexed - omit to fetch all pages"),
    page_size: int | None = typer.Option(None, "--page-size", "-z", help="Page size for results"),
    prt: bool = typer.Option(True, "--print", help="If result should be printed to the terminal", hidden=True),
):
    """
    List custom metrics data points for an entity
    """

    client = ctx.obj["client"]

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "page": page,
        "pageSize": page_size
    }

    # remove any params that are None
    params = {k: v for k, v in params.items() if v is not None}

    params = _convert_datetime_to_string(params)

    client.fetch_or_get("api/v1/eng-intel/custom-metrics/" + custom_metric_key + "/entity/" + tag, page, prt, params=params)

@app.command()
def add(
    ctx: typer.Context,
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    custom_metric_key: str = typer.Option(..., "--custom-metric-key", "-k", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    timestamp: datetime = typer.Option(datetime.now(), "--timestamp", "-s", help="Timestamp for the data point; cannot be earlier than 6 months", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    value: float = typer.Option(..., "--value", "-v", help="Value for the data point"),
):
    """
    Add a single custom metric data point for entity
    """

    client = ctx.obj["client"]

    data = {
        "timestamp": timestamp,
        "value": value
    }

    data = _convert_datetime_to_string(data)

    r = client.post("api/v1/eng-intel/custom-metrics/" + custom_metric_key + "/entity/" + tag, data=data)

@app.command()
def add_in_bulk(
    ctx: typer.Context,
    custom_metric_key: str = typer.Option(..., "--custom-metric-key", "-k", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    file_input: Annotated[typer.FileText, typer.Option("--file", "-f", help=" File containing custom event; can be passed as stdin with -, example: -f-")] = None,
    series: list[str] | None  = typer.Option(None, "--value", "-v", callback=_parse_key_value, help="List of timestamp=value pairs."),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
):
    """
    Add multiple custom metric data points for entity, can be provided in file, command line or combination of both
    """

    client = ctx.obj["client"]

    data = {
       "series": []
    }
    series_data = {
       "series": series
    }

    if file_input:
        data = json.loads("".join([line for line in file_input]))

    if series:
        for item in series:
           data["series"].append(item)

    r = client.post("api/v1/eng-intel/custom-metrics/" + custom_metric_key + "/entity/" + tag + "/bulk", data=data)

@app.command()
def delete(
    ctx: typer.Context,
    custom_metric_key: str = typer.Option(..., "--custom-metric-key", "-k", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    tag: str = typer.Option(..., "--tag", "-t", help="The tag (x-cortex-tag) or unique, auto-generated identifier for the entity."),
    start_date: datetime = typer.Option(None, "--start-date", "-s", help="Start date for the deletion (inclusive)", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
    end_date: datetime = typer.Option(None, "--end-date", "-e", help="End date for the deletion (inclusive)", formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]),
):
    """
    Delete custom metric data points for entity
    """

    client = ctx.obj["client"]

    params = {
       "startDate": start_date,
       "endDate": end_date
    }
    params = _convert_datetime_to_string(params)

    r = client.delete("api/v1/eng-intel/custom-metrics/" + custom_metric_key + "/entity/" + tag, params=params)
