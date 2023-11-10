"""
Tests for teams commands.
"""
from cortexapps_cli.cortex import cli

import json
import pytest
import sys

def _catalog_list(capsys):
    cli(["catalog", "list"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def test_dependencies_add(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-dependencies-add-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-dependencies-add-service"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_add_service.yaml"])

    if any(entity['tag'] == 'test-dependencies-add-dependency' for entity in json_data['entities']):
        cli(["dependencies", "delete-all", "-r", "test-dependencies-add-dependency"])
        cli(["catalog", "delete", "-t", "test-dependencies-add-dependency"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_add_dependency.yaml"])

    cli(["dependencies", "add", "-r", "test-dependencies-add-dependency", "-e",
          "test-dependencies-add-service", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies.json"])

def test_dependencies_delete(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-dependencies-delete-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-dependencies-delete-service"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_delete_service.yaml"])

    if any(entity['tag'] == 'test-dependencies-delete-dependencyy' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-dependencies-delete-dependencyy"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_delete_dependency.yaml"])

    cli(["dependencies", "add", "-r", "test-dependencies-delete-dependency", "-e",
          "test-dependencies-delete-service", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies.json"])
    cli(["dependencies", "delete", "-r", "test-dependencies-delete-dependency", "-e", "test-dependencies-delete-service", "-m", "GET", "-p", "/2.0/users/{username}"])

def test_dependencies_add_in_bulk(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-dependencies-bulk-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-dependencies-bulk-service"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_bulk_service.yaml"])

    if any(entity['tag'] == 'test-dependencies-bulk-dependency' for entity in json_data['entities']):
        cli(["dependencies", "delete-all", "-r", "test-dependencies-bulk-dependency"])
        cli(["catalog", "delete", "-t", "test-dependencies-bulk-dependency"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_bulk_dependency.yaml"])

    cli(["dependencies", "add", "-r", "test-dependencies-bulk-dependency", "-e",
          "test-dependencies-bulk-service", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies.json"])

def test_dependencies_get(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-dependencies-get-dependency' for entity in json_data['entities']):
        cli(["dependencies", "delete-all", "-r", "test-dependencies-get-dependency"])
        cli(["catalog", "delete", "-t", "test-dependencies-get-dependency"])

    if any(entity['tag'] == 'test-dependencies-get-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-dependencies-get-service"])

    cli(["catalog", "create", "-f", "tests/test_dependencies_get_service.yaml"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_get_dependency.yaml"])

    cli(["dependencies", "get", "-r", "test-dependencies-get-dependency", "-e", "test-dependencies-get-service", "-m", "GET", "-p", "/2.0/users/{username}"])

def test_dependencies_get_all(capsys):
    cli(["dependencies", "get-all", "-r", "dependency-service", "-o"])

def test_dependencies_update(capsys):
    cli(["catalog", "create", "-f", "tests/test_dependencies_update_service.yaml"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_update_dependency.yaml"])
    cli(["dependencies", "update", "-r", "dependency-service-update", "-e", "test-service-update", "-m", "GET", "-p", "/2.0/users/{username}", "-f", "tests/test_dependencies_update.json"])

def test_dependencies_delete_all(capsys):
    cli(["catalog", "create", "-f", "tests/test_dependencies_delete_all_service.yaml"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_delete_all_dependency.yaml"])
    cli(["dependencies", "delete-all", "-r", "dependency-service-delete-all"])

def test_dependencies_delete_in_bulk(capsys):
    json_data = _catalog_list(capsys)

    if any(entity['tag'] == 'test-dependencies-delete-in-bulk-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-dependencies-delete-in-bulk-service"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_delete_in_bulk_service.yaml"])

    if any(entity['tag'] == 'test-dependencies-delete-in-bulk-dependency' for entity in json_data['entities']):
        cli(["dependencies", "delete-all", "-r", "test-dependencies-delete-in-bulk-dependency"])
        cli(["catalog", "delete", "-t", "test-dependencies-delete-in-bulk-dependency"])
    cli(["catalog", "create", "-f", "tests/test_dependencies_delete_in_bulk_dependency.yaml"])

    cli(["dependencies", "add-in-bulk", "-f", "tests/test_dependencies_delete_in_bulk.json"])
    cli(["dependencies", "delete-in-bulk", "-f", "tests/test_dependencies_delete_in_bulk.json"])
