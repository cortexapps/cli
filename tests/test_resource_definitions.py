"""
Tests for resource-definitions commands.
"""
from cortexapps_cli.cortex import cli
import json
import sys

def test_resource_definitions_create(capsys):
    # Delete resource definition if it already exists.
    cli(["resource-definitions", "list"])
    out, err = capsys.readouterr()
    # Maybe a cleaner way to do this with json object?
    if (str(out).find('{"type":"test-resource-definition"') != -1):
        cli(["resource-definitions", "delete", "-t", "test-resource-definition"])
    cli(["resource-definitions", "create", "-f", "tests/test-resource-definition.json"])

def test_resource_definitions_list():
    cli(["resource-definitions", "list"])

def test_resource_definitions_get():
    cli(["resource-definitions", "get", "-t", "test-resource-definition"])

def test_resource_definitions_update():
    cli(["resource-definitions", "update", "-t", "test-resource-definition", "-f", "tests/test-resource-definition-update.json"])
