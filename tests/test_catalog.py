"""
Tests for the catalog methods.
"""

from cortexapps_cli.cortex import cli
import json
import pytest
import sys

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

def test_list_with_owners(capsys):
    cli(["catalog", "list", "-l", "-io", "-g", "corona-spokesperson"])
    out, err = capsys.readouterr()
    out = json.loads(out)

    found_service = False
    for entity in out['entities']:
        if entity['tag'] == "test-service":
           assert len(entity['links']) > 0
           assert len(entity['owners']) > 0
           found_service = True

    assert found_service

def test_list_descriptors(capsys, tmp_path):
    cli(["catalog", "list-descriptors", "-z", "1", "-p", "0", "-y"])
    out, err = capsys.readouterr()
    out = json.loads(out)

    f = tmp_path / "descriptor.yaml"
    f.write_text(out["descriptors"][0])

    # Should be able to have a dryrun validate the yaml
    cli(["catalog", "create", "-d", "-f", str(f)])

# Since gitops not set up for this service, it should return "Not Found".
# Kind of a cheap way out for this test, but it does validate the metod
# was accepted and returnd a value.
def test_gitops_logs(capsys):
    # Must be raised as exception, because of the expected 404 status code.
    with pytest.raises(SystemExit) as excinfo:
       cli(["catalog", "gitops-logs", "-t", "test-service"])
       out, err = capsys.readouterr()

       assert out == "Not Found"
       assert excinfo.value.code == 404

# Not checking any output because we cannot guarantee scorecards have
# been evaluated.
#
# Can change this in the future when there is a way to ensure that a
# scorecard has been evaluated.
def test_scorecard_scores(capsys):
    cli(["catalog", "scorecard-scores", "-t", "test-service"])
