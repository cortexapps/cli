"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

def _add_deploy():
    cli(["deploys", "add", "-t", "test-service", "-f", "tests/test_deploys.json"])

def test_deploys_add():
    _add_deploy()

def test_deploys_list():
    cli(["deploys", "list", "-t", "test-service"])

def test_deploys_delete():
    cli(["deploys", "delete", "-t", "test-service", "-s", "SHA-123456"])
    _add_deploy()

def test_deploys_delete_filter():
    cli(["deploys", "delete-filter", "-y", "DEPLOY"])
    _add_deploy()

def test_deploys_add():
    cli(["deploys", "delete-all"])
