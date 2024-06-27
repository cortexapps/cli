"""
Tests for groups commands.
"""
from cortexapps_cli.cortex import cli

def test_groups_add():
    cli(["groups", "add", "-t", "test-service", "-f", "tests/test-groups.json"])

def test_groups_get():
    cli(["groups", "get", "-t", "test-service"])

def test_groups_delete():
    cli(["groups", "delete", "-t", "test-service", "-f", "tests/test-groups.json"])
    cli(["groups", "get", "-t", "test-service"])
