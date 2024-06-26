from cortexapps_cli.cortex import cli

from contextlib import redirect_stdout
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from github import Auth
from github import Github
from string import Template
from types import SimpleNamespace
from unittest import mock
import io
import json
import os
import pytest
import random
import re
import requests
import sys
import tempfile
import textwrap
import time
import yaml
from feature_flag_check import *

def cli_command(capsys, args, output_type="json"):
    args = ["-q"] + args

    try:
        cli(args)
    except:
        captured = capsys.readouterr()
        print("cli_command: error: " + captured.err)

    out, err = capsys.readouterr()

    if output_type == "json":
        return json.loads(out)
    elif output_type == "text":
        return out

def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

def yesterday():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days = 1)
    return yesterday.strftime("%Y-%m-%dT%H:%M:%S")

def packages(capsys, packageCommand, packageType, version, name, tag):
    response = cli_command(capsys, ["packages", "list", "-t", tag])
    assert any(package['packageType'] == packageType and 
               package['version'] == version and
               package['name'] == name 
           for package in response), "Should find " + packageType + " package with name " + name + " and version " + version + " for entity " + tag

    cli(["packages", packageCommand, "delete", "-t", tag, "-n", name])
    response = cli_command(capsys, ["packages", "list", "-t", tag])
    assert not any(package['packageType'] == packageType and 
               package['name'] == name 
           for package in response), "Should not find " + packageType + " package with name " + name
