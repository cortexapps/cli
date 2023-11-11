"""
Tests for the catalog methods.
"""
from cortexapps_cli.cortex import cli
import json
import pytest
import sys

def _catalog_list(capsys):
    cli(["catalog", "list"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def test_catalog(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-catalog-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-catalog-service"])
    cli(["catalog", "create", "-f", "tests/test_catalog_service.yaml"])

    cli(["catalog", "descriptor", "-y", "-t", "test-catalog-service"])
    cli(["catalog", "archive", "-t", "test-catalog-service"])
    cli(["catalog", "unarchive", "-t", "test-catalog-service"])
    cli(["catalog", "details", "-t", "test-catalog-service"])

def test_catalog_owners(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-catalog-owners-team' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-catalog-owners-team"])
    cli(["catalog", "create", "-f", "tests/test_catalog_owners_team.yaml"])

    if any(entity['tag'] == 'test-catalog-owners-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-catalog-owners-service"])
    cli(["catalog", "create", "-f", "tests/test_catalog_owners_service.yaml"])

    cli(["catalog", "list", "-o", "test-catalog-owners-team" ])
    out, err = capsys.readouterr()
    assert "test-catalog-owners-service" in out

def test_catalog_groups(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-catalog-groups-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-catalog-groups-service"])
    cli(["catalog", "create", "-f", "tests/test_catalog_groups_service.yaml"])

    cli(["catalog", "list", "-g", "test-catalog-owners-group", "-d", "1", "-t", "service", "-a", "-m" ])
    out, err = capsys.readouterr()
    assert "test-catalog-groups-service" in out

def test_dryrun(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli(["catalog", "create", "-d", "-f", "tests/test_catalog-invalid-service.yaml"])
        out, err = capsys.readouterr()
        assert json.loads(out)['type'] == "BAD_REQUEST"
