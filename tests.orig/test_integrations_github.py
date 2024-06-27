"""
Tests for github integration commands.
"""
from cortexapps_cli.cortex import cli
import os
import pytest
import responses

# Since responses are all mocked and no data validation is done by the CLI --
# we let the API handle validation -- we don't need valid input files.
def _dummy_file(tmp_path):
    f = tmp_path / "test.json"
    f.write_text("foobar")
    return f

@responses.activate
def test_integrations_github_add_personal(capsys, tmp_path):
    f = _dummy_file(tmp_path)

    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/personal", status=200)
    cli(["integrations", "github", "add-personal", "-f", str(f)])

@responses.activate
def test_integrations_github_update_personal(capsys, tmp_path):
    f = _dummy_file(tmp_path)

    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/personal/pt-001", status=200)
    cli(["integrations", "github", "update-personal", "-a", "pt-001", "-f", str(f)])

@responses.activate
def test_integrations_github_get_personal(capsys, tmp_path):
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/personal/pt-001", status=200)
    cli(["integrations", "github", "get-personal", "-a", "pt-001"])

@responses.activate
def test_integrations_github_add(capsys, tmp_path):
    f = _dummy_file(tmp_path)

    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/app", status=200)
    cli(["integrations", "github", "add", "-f", str(f)])

@responses.activate
def test_integrations_github_get(capsys, tmp_path):
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/app/pt-001", status=200)
    cli(["integrations", "github", "get", "-a", "pt-001"])

@responses.activate
def test_integrations_github_get_all(capsys, tmp_path):
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations", status=200)
    cli(["integrations", "github", "get-all"])

@responses.activate
def test_integrations_github_get_default(capsys, tmp_path):
    responses.add(responses.GET, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/default-configuration", status=200)
    cli(["integrations", "github", "get-default"])

@responses.activate
def test_integrations_github_validate(capsys, tmp_path):
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/validate/pt-001", status=200)
    cli(["integrations", "github", "validate", "-a", "pt-001"])

@responses.activate
def test_integrations_github_validate_all(capsys, tmp_path):
    responses.add(responses.POST, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/validate", status=200)
    cli(["integrations", "github", "validate-all"])

@responses.activate
def test_integrations_github_update(capsys, tmp_path):
    f = _dummy_file(tmp_path)

    responses.add(responses.PUT, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations/app/pt-001", status=200)
    cli(["integrations", "github", "update", "-a", "pt-001", "-f", str(f)])

@responses.activate
def test_integrations_github_delete_all():
    responses.add(responses.DELETE, os.getenv("CORTEX_BASE_URL") + "/api/v1/github/configurations", status=200)
    cli(["integrations", "github", "delete-all"])
