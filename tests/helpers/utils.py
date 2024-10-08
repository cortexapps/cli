from cortexapps_cli.cli import app
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json
from typer.testing import CliRunner

runner = CliRunner()

def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

def yesterday():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days = 1)
    return yesterday.strftime("%Y-%m-%dT%H:%M:%S")

def json_response(params):
    print("params = " + str(params))
    response = runner.invoke(app, params)
    return json.loads(response.stdout)

def cli(params):
    runner.invoke(app, params)
