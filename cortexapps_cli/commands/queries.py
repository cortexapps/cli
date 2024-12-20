import json
from rich import print_json
import typer
from typing_extensions import Annotated

app = typer.Typer(help="Queries commands", no_args_is_help=True)

@app.command()
def run(
    ctx: typer.Context,
    query_input: Annotated[typer.FileText, typer.Option(..., "--file", "-f", help=" File containing JSON-formatted CQL query; can be passed as stdin with -, example: -f-")] = None,
    wait: bool = typer.Option(False, "--wait", "-w", help="Optional; wait for query to complete"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Page size for results")
):
    """
    Run CQL query
    """

    client = ctx.obj["client"]

    data = {}
    data['query'] = query_input.read()

    r = client.post("api/v1/queries", data=data)

    if wait:
        job_id = r['jobId']
        sleep_interval = 2
        max_attempts = int(timeout) // sleep_interval

        done = False
        for attempt in range(1, max_attempts):
            r = client.get("api/v1/queries/" + job_id)
            if r['status'] == "DONE":
                done = True
                break
            else:
                if attempt == max_attempts:
                    break
                time.sleep(sleep_interval)

        if not done:
            print("failed to find job id " + job_id + " in DONE state within " + str(args.timeout) + " seconds")
            print(str(out))
            sys.exit(2)
        else:
            print_json(data=r)
    else:
        print_json(data=r)
     

@app.command()
def get(
    ctx: typer.Context,
    job_id: str = typer.Option(..., "--job-id", "-j", help="The job id of the CQL query")
):
    """
    Retrieve the status and results of a CQL query
    """

    client = ctx.obj["client"]

    r = client.get("api/v1/queries/" + job_id)
    print_json(data=r)
