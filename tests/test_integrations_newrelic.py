"""
Tests for newrelic integration commands.
"""
from cortexapps_cli.cortex import cli
from string import Template
import json
import os
import pytest
import responses
import sys

newrelic_account_id = 123
newrelic_personal_key = json.dumps("fakeKey")

def _newrelic_input(tmp_path):
    f = tmp_path / "test_integrations_newrelic_add.json"
    template = Template("""
        {
          "accountId": ${newrelic_account_id},
          "alias": "test",
          "isDefault": true,
          "personalKey": ${newrelic_personal_key},
          "region": "US"
        }
        """)
    content = template.substitute(newrelic_account_id=newrelic_account_id, newrelic_personal_key=newrelic_personal_key)
    sys.stdout.write(content)
    f.write_text(content)
    return f

def test_integrations_newrelic_add(tmp_path):
    f = _newrelic_input(tmp_path)

    cli(["integrations", "newrelic", "delete-all"])
    cli(["integrations", "newrelic", "add", "-f", str(f)])
    cli(["integrations", "newrelic", "get", "-a", "test"])
    cli(["integrations", "newrelic", "get-all"])
    cli(["integrations", "newrelic", "get-default"])

    cli(["integrations", "newrelic", "update", "-a", "test", "-f", str(f)])
    cli(["integrations", "newrelic", "delete", "-a", "test"])

    f = tmp_path / "test_integrations_newrelic_update_multiple.json"
    template = Template("""
        {
          "configurations": [
           {
             "accountId": ${newrelic_account_id},
             "alias": "test-1",
             "isDefault": false,
             "personalKey": ${newrelic_personal_key},
             "region": "US"
           },
           {
             "accountId": ${newrelic_account_id},
             "alias": "test-2",
             "isDefault": false,
             "personalKey": ${newrelic_personal_key},
             "region": "US"
           }
          ]
        }
        """)
    content = template.substitute(newrelic_account_id=newrelic_account_id, newrelic_personal_key=newrelic_personal_key)
    f.write_text(content)
    cli(["integrations", "newrelic", "add-multiple", "-f", str(f)])
    cli(["integrations", "newrelic", "delete-all"])

@responses.activate
def test_integrations_newrelic_validate(tmp_path):
    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/newrelic/configuration/validate/test", json={'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}, status=200)
    cli(["integrations", "newrelic", "validate", "-a", "test"])

    responses.add(responses.POST, "https://api.getcortexapp.com/api/v1/newrelic/configuration/validate", json=[ { 'alias': 'test', 'isValid': json.dumps("true"), 'message': 'someMessage'}], status=200)
    cli(["integrations", "newrelic", "validate-all"])
