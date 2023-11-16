"""
Tests for docs commands.
"""
from cortexapps_cli.cortex import cli

def test_docs():
    cli(["docs", "update", "-t", "cli-test-service", "-f", "tests/test_docs.yaml"])

    cli(["docs", "get", "-t", "cli-test-service"])

    cli(["docs", "delete", "-t", "cli-test-service"])
