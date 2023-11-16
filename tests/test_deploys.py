"""
Tests for deploys commands.
"""
from cortexapps_cli.cortex import cli

def _add_deploy():
    cli(["deploys", "add", "-t", "cli-test-service", "-f", "tests/test_deploys.json"])

def test_deploys_add():
    _add_deploy()

    cli(["deploys", "list", "-t", "cli-test-service"])

    cli(["deploys", "delete", "-t", "cli-test-service", "-s", "SHA-123456"])
    _add_deploy()

    cli(["deploys", "delete-filter", "-y", "DEPLOY"])
    _add_deploy()

    cli(["deploys", "delete-all"])
