"""
Tests for deploys commands.
"""
from cortexapps_cli.cortex import cli

import json

def _catalog_list(capsys):
    cli(["catalog", "list"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def test_deploys(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-deploys-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-deploys-service"])
    cli(["catalog", "create", "-f", "tests/test_deploys_service.yaml"])

    cli(["deploys", "delete-all"])

    cli(["deploys", "add", "-t", "test-deploys-service", "-f", "tests/test_deploys.json"])
    cli(["deploys", "delete", "-t", "test-deploys-service", "-s", "SHA-123456"])
    cli(["deploys", "delete-filter", "-y", "DEPLOY"])
