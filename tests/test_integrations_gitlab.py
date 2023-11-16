"""
Tests for gitlab integration commands.
"""
from cortexapps_cli.cortex import cli
import os
import sys
from string import Template

def test_integrations_gitlab_add(tmp_path):
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

    cli(["integrations", "gitlab", "get", "-a", "cortex-test"])

    cli(["integrations", "gitlab", "get-all"])

    cli(["integrations", "gitlab", "get-default"])

    cli(["integrations", "gitlab", "validate", "-a", "cortex-test"])

    cli(["integrations", "gitlab", "validate-all"])

    cli(["integrations", "gitlab", "update", "-a", "cortex-test", "-f", "tests/test_integrations_gitlab_update.json"])

    cli(["integrations", "gitlab", "add-multiple", "-f", "tests/test_integrations_gitlab_add_multiple.json"])

    cli(["integrations", "gitlab", "delete", "-a", "cortex-test-2"])

    cli(["integrations", "gitlab", "delete-all"])
