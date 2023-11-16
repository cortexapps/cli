"""
Tests for github integration commands.
"""
from cortexapps_cli.cortex import cli
import os
from string import Template
import json
import pytest

def github_personal_input(tmp_path):
    gh_pat = os.getenv('GH_PAT')
    f = tmp_path / "test_integrations_github_add_personal.json"
    template = Template("""
        {
          "accessToken": "${gh_pat}",
          "alias": "github-personal-test-001",
          "isDefault": false
        }
        """)
    content = template.substitute(gh_pat=gh_pat)
    f.write_text(content)
    return f

def github_app_input(tmp_path):
    gh_app_id = os.getenv('GH_APP_ID')
    gh_client_id = os.getenv('GH_CLIENT_ID')
    gh_client_secret = os.getenv('GH_CLIENT_SECRET')
    gh_private_key = os.getenv('GH_PRIVATE_KEY')
    f = tmp_path / "test_integrations_github_add.json"
    template = Template("""
        {
          "alias": "github-test-3",
          "appUrl": "https://github.com/apps/cortex-app",
          "applicationId": "${gh_app_id}",
          "clientId": "${gh_client_id}",
          "clientSecret": "${gh_client_secret}",
          "isDefault": false,
          "privateKey": "${gh_private_key}"
        }
        """)
    content = template.substitute(gh_app_id=gh_app_id, gh_client_id=gh_client_id, gh_client_secret=gh_client_secret, gh_private_key=gh_private_key)
    f.write_text(content)
    return f

def test_integrations_github_personal(capsys, tmp_path):
    cli(["integrations", "github", "get-personal", "-a", "github-personal-test-001"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    if (out['type'] != "NOT_FOUND"):
        cli(["integrations", "github", "delete-personal", "-a", "github-personal-test-001"])

    f = github_personal_input(tmp_path)
    cli(["integrations", "github", "add-personal", "-f", str(f)])

def test_integrations_github(tmp_path, capsys):
    cli(["integrations", "github", "get", "-a", "github-test-3"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    if (out['type'] != "NOT_FOUND"):
        cli(["integrations", "github", "delete", "-a", "github-test-3"])

    f = github_app_input(tmp_path)
    cli(["integrations", "github", "add", "-f", str(f)])

    cli(["integrations", "github", "get", "-a", "github-test-3"])

    cli(["integrations", "github", "get-personal", "-a", "github-personal-test-001"])

    cli(["integrations", "github", "get-all"])

    cli(["integrations", "github", "get-default"])

    cli(["integrations", "github", "validate", "-a", "cortex-test"])

    cli(["integrations", "github", "validate-all"])

    f = github_personal_input(tmp_path)
    cli(["integrations", "github", "update-personal", "-a", "github-personal-test-001", "-f", str(f)])

    cli(["integrations", "github", "update", "-a", "github-test-3", "-f", "tests/test_integrations_github_update.json"])

# Intentionally missing delete-all test because I didn't want to destroy my test env
# Can add this in once we have a better process, an automated process to create github apps
# cli(["integrations", "github", "delete-all"])
