"""
Tests for coralogix integration commands.
"""
from cortexapps_cli.cortex import cli
from string import Template
import json
import os
import pytest
import responses

coralogix_api_key = json.dumps("fakeKey")

def _coralogix_input(tmp_path):
    f = tmp_path / "test_integrations_coralogix_add.json"
    template = Template("""
        {
          "alias": "test",
          "apiKey": ${coralogix_api_key},
          "isDefault": true,
          "region": "US1"
        }
        """)
    content = template.substitute(coralogix_api_key=coralogix_api_key)
    f.write_text(content)
    return f

def test_integrations_coralogix_add(tmp_path):
    f = _coralogix_input(tmp_path)

    cli(["integrations", "coralogix", "delete-all"])
    cli(["integrations", "coralogix", "add", "-f", str(f)])
    cli(["integrations", "coralogix", "get", "-a", "test"])
    cli(["integrations", "coralogix", "get-all"])
    cli(["integrations", "coralogix", "get-default"])

    cli(["integrations", "coralogix", "update", "-a", "test", "-f", str(f)])
    cli(["integrations", "coralogix", "delete", "-a", "test"])

    f = tmp_path / "test_integrations_coralogix_update_multiple.json"
    template = Template("""
        {
          "configurations": [
            {
              "alias": "test",
              "apiKey": ${coralogix_api_key},
              "isDefault": true,
              "region": "US1"
            },
            {
              "alias": "test-2",
              "apiKey": ${coralogix_api_key},
              "isDefault": true,
              "region": "US2"
            }
          ]
        }
        """)
    content = template.substitute(coralogix_api_key=coralogix_api_key)
    f.write_text(content)
    cli(["integrations", "coralogix", "add-multiple", "-f", str(f)])
    cli(["integrations", "coralogix", "delete-all"])

@responses.activate
def test_integrations_coralogix_validate(tmp_path):
    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/coralogix/configuration/validate/test", json={'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}, status=200)
    cli(["integrations", "coralogix", "validate", "-a", "test"])

    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/coralogix/configuration/validate", json=[ { 'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}], status=200)
    cli(["integrations", "coralogix", "validate-all"])
