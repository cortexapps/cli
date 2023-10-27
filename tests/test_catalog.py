"""
Tests for the catalog methods.
"""
from unittest.mock import patch
import json
import sys
import os
import pytest
from cortexapps_cli.cortex import cli
import yaml
import pytest

def test_create_service(capsys):
    cli(["catalog", "create", "-f", "tests/test_catalog_service.yaml"])

def test_retrieve_service(capsys):
    cli(["catalog", "descriptor", "-y", "-t", "test-service"])
    out, err = capsys.readouterr()
    with open('tests/test_catalog_service.yaml', 'r') as f:
       y = f.read()
    assert out == y, "Contents of source yaml and retrieved descriptor should be identical"

def test_dryrun(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli(["catalog", "create", "-d", "-f", "tests/test_catalog-invalid-service.yaml"])
        out, err = capsys.readouterr()
        assert json.loads(out)['type'] == "BAD_REQUEST"

def test_details(capsys):
    cli(["catalog", "details", "-t", "test-service"])

def test_list(capsys):
    cli(["catalog", "list"])

def test_list_with_parms(capsys):
    cli(["catalog", "list", "-g", "corona-spokesperson", "-d", "1", "-t", "service", "-a", "-m" ])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert str(out['entities'][0]['tag']) == "test-service", "x-cortex-tag should be test-service"
    assert not(out['entities'][0]['metadata'][0]["key"] is None), "Custom metadata should have been in result"

def test_archive():
    cli(["catalog", "archive", "-t", "test-service"])

def test_unarchive():
    cli(["catalog", "unarchive", "-t", "test-service"])

def test_list_by_team(capsys):
    cli(["catalog", "list", "-o", "test-team-1" ])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert str(out['entities'][0]['tag']) == "test-service"

