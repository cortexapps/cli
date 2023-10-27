"""
Tests for docs commands.
"""
from cortexapps_cli.cortex import cli

def test_docs_update():
    cli(["docs", "update", "-t", "test-service", "-f", "tests/test_docs.yaml"])

def test_docs_get():
    cli(["docs", "get", "-t", "test-service"])

def test_docs_delete():
    cli(["docs", "delete", "-t", "test-service"])
