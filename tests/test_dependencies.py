"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

def test_dependencies(capsys):
    cli(["dependencies", "delete-all", "-r", "dependency-service"])
    cli(["dependencies", "add", "-r", "dependency-service", "-e",
          "test-service", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies.json"])

    cli(["dependencies", "delete", "-r", "dependency-service", "-e", "test-service", "-m", "GET", "-p", "/2.0/users/{username}"])

    cli(["dependencies", "add-in-bulk", "-f", "tests/test_dependencies_bulk.json"])

    cli(["dependencies", "get", "-r", "dependency-service", "-e", "test-service", "-m", "GET", "-p", "/2.0/users/{username}"])

    cli(["dependencies", "get-all", "-r", "dependency-service", "-o"])

    cli(["dependencies", "update", "-r", "dependency-service", "-e", "test-service", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies_update.json"])

    cli(["dependencies", "add-in-bulk", "-f", "tests/test_dependencies_bulk.json"])
    cli(["dependencies", "delete-in-bulk", "-f", "tests/test_dependencies_bulk.json"])
    cli(["dependencies", "delete-all", "-r", "dependency-service"])
