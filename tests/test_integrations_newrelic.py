@pytest.mark.skip(reason="Skipping until I can figure out how to install community newrelic and use ngrok3")
"""
Tests for newrelic integration commands.
"""
from cortexapps_cli.cortex import cli
from string import Template
import os

newrelic_account_id = os.getenv('NEWRELIC_ACCOUNT_ID')
newrelic_personal_key = os.getenv('NEWRELIC_PERSONAL_KEY')

def _newrelic_input(tmp_path):
    f = tmp_path / "test_integrations_newrelic_add.json"
    template = Template("""
        {
          "accountId": ${newrelic_account_id},
          "alias": "test",
          "isDefault": true,
          "personalKey": "${newrelic_personal_key}",
          "region": "US"
        }
        """)
    content = template.substitute(newrelic_account_id=newrelic_account_id, newrelic_personal_key=newrelic_personal_key)
    f.write_text(content)
    return f

def test_integrations_newrelic_add(tmp_path):
    cli(["integrations", "newrelic", "delete-all"])
    f = _newrelic_input(tmp_path)
    cli(["integrations", "newrelic", "add", "-f", str(f)])

def test_integrations_newrelic_get():
    cli(["integrations", "newrelic", "get", "-a", "test"])

def test_integrations_newrelic_get_all():
    cli(["integrations", "newrelic", "get-all"])

def test_integrations_newrelic_get_default():
    cli(["integrations", "newrelic", "get-default"])

def test_integrations_newrelic_validate():
    cli(["integrations", "newrelic", "validate", "-a", "test"])

def test_integrations_newrelic_validate_all():
    cli(["integrations", "newrelic", "validate-all"])

def test_integrations_newrelic_update(tmp_path):
    f = _newrelic_input(tmp_path)
    cli(["integrations", "newrelic", "update", "-a", "test", "-f", str(f)])

def test_integrations_newrelic_delete():
    cli(["integrations", "newrelic", "delete", "-a", "test"])

def test_integrations_newrelic_update_multiple(tmp_path):
    f = tmp_path / "test_integrations_newrelic_update_multiple.json"
    template = Template("""
        {
          "configurations": [
           {
             "accountId": ${newrelic_account_id},
             "alias": "test-1",
             "isDefault": false,
             "personalKey": "${newrelic_personal_key}",
             "region": "US"
           },
           {
             "accountId": ${newrelic_account_id},
             "alias": "test-2",
             "isDefault": false,
             "personalKey": "${newrelic_personal_key}",
             "region": "US"
           }
          ]
        }
        """)
    content = template.substitute(newrelic_account_id=newrelic_account_id, newrelic_personal_key=newrelic_personal_key)
    f.write_text(content)
    cli(["integrations", "newrelic", "add-multiple", "-f", str(f)])

def test_integrations_newrelic_delete_all():
    cli(["integrations", "newrelic", "delete-all"])


