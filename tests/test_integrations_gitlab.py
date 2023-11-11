"""
Tests for gitlab integration commands.
"""
from cortexapps_cli.cortex import cli
import json
import os
from string import Template
import sys

def _gitlab_all(capsys):
    cli(["integrations", "gitlab", "get-all"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def test_integrations_gitlab(tmp_path, capsys):
    json_data = _gitlab_all(capsys)
    if json_data:
        cli(["integrations", "gitlab", "delete-all"])

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
    cli(["integrations", "gitlab", "validate", "-a", "cortex-test"])
    cli(["integrations", "gitlab", "get", "-a", "cortex-test"])
    cli(["integrations", "gitlab", "add-multiple", "-f", "tests/test_integrations_gitlab_add_multiple.json"])
    cli(["integrations", "gitlab", "get-default"])
    cli(["integrations", "gitlab", "update", "-a", "cortex-test", "-f", "tests/test_integrations_gitlab_update.json"])
    cli(["integrations", "gitlab", "validate-all"])
    cli(["integrations", "gitlab", "delete", "-a", "cortex-test-2"])
    cli(["integrations", "gitlab", "delete-all"])
