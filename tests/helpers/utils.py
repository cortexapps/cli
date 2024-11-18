from cortexapps_cli.cli import app
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from enum import Enum
import json
import os
import pytest
from typer.testing import CliRunner
from unittest import mock

runner = CliRunner()

class ReturnType(str, Enum):
    JSON = "JSON"
    RAW = "RAW"
    STDOUT = "STDOUT"

def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

def yesterday():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days = 1)
    return yesterday.strftime("%Y-%m-%dT%H:%M:%S")

def cli(params, return_type=ReturnType.JSON):
    if not isinstance(return_type, ReturnType):
        raise TypeError('return_type must be an instance of ReturnType Enum')

    result = runner.invoke(app, params)

    match return_type:
        case ReturnType.JSON:
            if result.stdout == "":
                return json.loads('{}')
            else:
                return json.loads(result.stdout)
        case ReturnType.RAW:
            return result
        case ReturnType.STDOUT:
            return result.stdout
        case ReturnType.STDERR:
            return result.stderr
