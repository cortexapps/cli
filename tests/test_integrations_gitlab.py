"""
Tests for gitlab integration commands.
"""
from cortexapps_cli.cortex import cli
import os
import sys
from string import Template

def test_integrations_gitlab_delete_all():
    cli(["integrations", "gitlab", "delete-all"])

def test_integrations_gitlab_add(tmp_path):
    gitlab_personal_token = os.getenv('GITLAB_PERSONAL_TOKEN')
    f = tmp_path / "test_integrations_gitlab_add.json"
    template = Template("""{
          "alias": "cortex-test",
          "groupNames": [
          ],
          "hidePersonalProjects": false,
          "isDefault": true,
          "personalAccessToken": "${gitlab_personal_token}"
        }
        """)
    content = template.substitute(gitlab_personal_token=gitlab_personal_token)
    f.write_text(content)
    cli(["integrations", "gitlab", "add", "-f", str(f)])

def test_integrations_gitlab_get():
    cli(["integrations", "gitlab", "get", "-a", "cortex-test"])

def test_integrations_gitlab_get_all():
    cli(["integrations", "gitlab", "get-all"])

def test_integrations_gitlab_get_default():
    cli(["integrations", "gitlab", "get-default"])

def test_integrations_gitlab_validate():
    cli(["integrations", "gitlab", "validate", "-a", "cortex-test"])

def test_integrations_gitlab_validate_all():
    cli(["integrations", "gitlab", "validate-all"])

def test_integrations_gitlab_update():
    cli(["integrations", "gitlab", "update", "-a", "cortex-test", "-f", "tests/test_integrations_gitlab_update.json"])

def test_integrations_gitlab_add_mutiple():
    cli(["integrations", "gitlab", "add-multiple", "-f", "tests/test_integrations_gitlab_add_multiple.json"])

def test_integrations_gitlab_delete():
    cli(["integrations", "gitlab", "delete", "-a", "cortex-test-2"])

def test_integrations_gitlab_delete_all():
    cli(["integrations", "gitlab", "delete-all"])
