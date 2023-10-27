"""
Tests for custom-data commands.
"""
from cortexapps_cli.cortex import cli
import json

def test_custom_data_add():
    cli(["custom-data", "add", "-t", "test-service", "-f", "tests/test-custom-data.json"])

def test_custom_data_list():
    cli(["custom-data", "list", "-t", "test-service"])

def test_custom_data_get():
    cli(["custom-data", "get", "-t", "test-service", "-k", "testField"])

def test_custom_data_bulk():
    cli(["custom-data", "bulk", "-f", "tests/test-custom-data-bulk.json"])

def test_custom_data_bulk_array():
    cli(["custom-data", "bulk", "-f", "tests/test-custom-data-array.json"])

def test_custom_data_key(capsys):
    # Test for https://cortex1.atlassian.net/browse/CET-4642
    cli(["custom-data", "get", "-t", "test-service", "-k", "checklist"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert str(out['value']['pii']) == "n/a"
