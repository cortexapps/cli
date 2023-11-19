"""
Tests for launchdarkly integration commands.
"""
from cortexapps_cli.cortex import cli
from string import Template
import json
import os
import pytest
import responses

launchdarkly_api_key = json.dumps("fakeKey")

def _launchdarkly_input(tmp_path):
    f = tmp_path / "test_integrations_launchdarkly_add.json"
    template = Template("""
        {
          "alias": "test",
          "apiKey": ${launchdarkly_api_key},
          "environment": "DEFAULT",
          "isDefault": true
        }
        """)
    content = template.substitute(launchdarkly_api_key=launchdarkly_api_key)
    f.write_text(content)
    return f

def test_integrations_launchdarkly_add(tmp_path):
    f = _launchdarkly_input(tmp_path)

    cli(["integrations", "launchdarkly", "delete-all"])
    cli(["integrations", "launchdarkly", "add", "-f", str(f)])
    cli(["integrations", "launchdarkly", "get", "-a", "test"])
    cli(["integrations", "launchdarkly", "get-all"])
    cli(["integrations", "launchdarkly", "get-default"])

    cli(["integrations", "launchdarkly", "update", "-a", "test", "-f", str(f)])
    cli(["integrations", "launchdarkly", "delete", "-a", "test"])

    f = tmp_path / "test_integrations_launchdarkly_update_multiple.json"
    template = Template("""
        {
          "configurations": [
            {
              "alias": "test",
              "apiKey": ${launchdarkly_api_key},
              "environment": "DEFAULT",
              "isDefault": true
            },
            {
              "alias": "test-2",
              "apiKey": ${launchdarkly_api_key},
              "environment": "FEDERAL",
              "isDefault": false
            }
          ]
        }
        """)
    content = template.substitute(launchdarkly_api_key=launchdarkly_api_key)
    f.write_text(content)
    cli(["integrations", "launchdarkly", "add-multiple", "-f", str(f)])
    cli(["integrations", "launchdarkly", "delete-all"])

@responses.activate
def test_integrations_launchdarkly_validate(tmp_path):
    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/launchdarkly/configuration/validate/test", json={'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}, status=200)
    cli(["integrations", "launchdarkly", "validate", "-a", "test"])

    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/launchdarkly/configuration/validate", json=[ { 'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}], status=200)
    cli(["integrations", "launchdarkly", "validate-all"])
