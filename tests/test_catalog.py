"""
Tests for the catalog methods.
"""

from cortexapps_cli.cortex import cli
import json
import pytest

def test_catalog_create_service(capsys):
    cli(["catalog", "create", "-f", "tests/test_catalog_create_service.yaml"])

def test_retrieve_service(capsys):
    cli(["catalog", "descriptor", "-y", "-t", "cli-test-service"])

def test_dryrun(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli(["catalog", "create", "-d", "-f", "tests/test_catalog-invalid-service.yaml"])
        out, err = capsys.readouterr()
        assert json.loads(out)['type'] == "BAD_REQUEST"

def test_details(capsys):
    cli(["catalog", "details", "-t", "cli-test-service"])

def test_list(capsys):
    cli(["catalog", "list"])

def test_list_with_parms(capsys):
    cli(["catalog", "list", "-g", "corona-spokesperson", "-d", "1", "-t", "service", "-a", "-m" ])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert any(service['tag'] == 'cli-test-service-with-groups' for service in out['entities'])
    assert not(out['entities'][0]['metadata'][0]["key"] is None), "Custom metadata should have been in result"

# Archiving a service can impact it from being seen by other operations.  Should probably be done with a separate
# service
def test_archive():
    cli(["catalog", "archive", "-t", "cli-test-service"])
    cli(["catalog", "unarchive", "-t", "cli-test-service"])

def test_list_by_team(capsys):
    cli(["catalog", "list", "-o", "test-team-1" ])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert any(service['tag'] == 'cli-test-service-with-groups' for service in out['entities'])
