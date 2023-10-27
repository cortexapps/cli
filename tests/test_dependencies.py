"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

def test_dependencies_add(capsys):
    # TODO: check if dependency already exits before trying to create it
    cli(["catalog", "create", "-f", "tests/test_dependencies_dependency_service.yaml"])
    cli(["dependencies", "add", "-r", "dependency-service", "-e",
          "test-service", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies.json"])

def test_dependencies_delete(capsys):
    cli(["dependencies", "delete", "-r", "dependency-service", "-e", "test-service", "-m", "GET", "-p", "/2.0/users/{username}"])

def test_dependencies_add_in_bulk(capsys):
    cli(["dependencies", "add-in-bulk", "-f", "tests/test_dependencies_bulk.json"])

def test_dependencies_get(capsys):
    cli(["dependencies", "get", "-r", "dependency-service", "-e", "test-service", "-m", "GET", "-p", "/2.0/users/{username}"])

def test_dependencies_get_all(capsys):
    cli(["dependencies", "get-all", "-r", "dependency-service", "-o"])

def test_dependencies_update(capsys):
    cli(["dependencies", "update", "-r", "dependency-service", "-e", "test-service", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies_update.json"])

def test_dependencies_delete_all(capsys):
    cli(["dependencies", "delete-all", "-r", "dependency-service"])

def test_dependencies_delete_in_bulk(capsys):
    cli(["dependencies", "add-in-bulk", "-f", "tests/test_dependencies_bulk.json"])
    cli(["dependencies", "delete-in-bulk", "-f", "tests/test_dependencies_bulk.json"])
