"""
Tests for sonarqube integration commands.
"""
from cortexapps_cli.cortex import cli
from string import Template
import os
import pytest

sonarqube_host = os.getenv('SONARQUBE_HOST')
sonarqube_personal_token = os.getenv('SONARQUBE_PERSONAL_TOKEN')

def _sonarqube_input(tmp_path):
    f = tmp_path / "test_integrations_sonarqube_add.json"
    template = Template("""
        {
          "alias": "cortex-test",
          "host": "${sonarqube_host}",
          "isDefault": true,
          "token": "${sonarqube_personal_token}"
        }
       """)
    content = template.substitute(sonarqube_host=sonarqube_host, sonarqube_personal_token=sonarqube_personal_token)
    f.write_text(content)
    return f

def test_integrations_sonarqube_delete_all():
    cli(["integrations", "sonarqube", "delete-all"])

def test_integrations_sonarqube_add(tmp_path):
    f = _sonarqube_input(tmp_path)
    cli(["integrations", "sonarqube", "add", "-f", str(f)])

def test_integrations_sonarqube_get():
    cli(["integrations", "sonarqube", "get", "-a", "cortex-test"])

def test_integrations_sonarqube_get_all():
    cli(["integrations", "sonarqube", "get-all"])

def test_integrations_sonarqube_get_default():
    cli(["integrations", "sonarqube", "get-default"])

@pytest.mark.skip(reason="Skipping until I can figure out how to install community sonarqube and use ngrok3")
def test_integrations_sonarqube_validate():
    cli(["integrations", "sonarqube", "validate", "-a", "cortex-test"])

@pytest.mark.skip(reason="Skipping until I can figure out how to install community sonarqube and use ngrok3")
def test_integrations_sonarqube_validate_all():
    cli(["integrations", "sonarqube", "validate-all"])

def test_integrations_sonarqube_update(tmp_path):
    f = _sonarqube_input(tmp_path)
    cli(["integrations", "sonarqube", "update", "-a", "cortex-test", "-f", str(f)])

def test_integrations_sonarqube_delete():
    cli(["integrations", "sonarqube", "delete", "-a", "cortex-test"])

def test_integrations_sonarqube_add_multiple(tmp_path):
    f = tmp_path / "test_integrations_sonarqube_add_multiple.json"
    template = Template("""
        {
          "configurations": [
           {
             "alias": "cortex-test-2",
             "host": "${sonarqube_host}",
             "isDefault": true,
             "token": "${sonarqube_personal_token}"
           },
           {
             "alias": "cortex-test-3",
             "host": "${sonarqube_host}",
             "isDefault": true,
             "token": "${sonarqube_personal_token}"
           }
          ]
        }
       """)
    content = template.substitute(sonarqube_host=sonarqube_host, sonarqube_personal_token=sonarqube_personal_token)
    f.write_text(content)
    cli(["integrations", "sonarqube", "add-multiple", "-f", str(f)])
