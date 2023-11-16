"""
Tests for custom-data commands.
"""
from cortexapps_cli.cortex import cli
import json

def test_custom_data():
    cli(["custom-data", "add", "-t", "test-service", "-f", "tests/test-custom-data.json"])
    cli(["custom-data", "list", "-t", "test-service"])

def test_custom_data_bulk():
    cli(["custom-data", "bulk", "-f", "tests/test-custom-data-bulk.json"])

def test_custom_data_bulk_array():
    cli(["custom-data", "bulk", "-f", "tests/test-custom-data-array.json"])

def test_custom_data_get():
    cli(["custom-data", "get", "-t", "test-service", "-k", "foo"])
