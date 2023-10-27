"""
Tests for prometheus integration commands.
"""
from cortexapps_cli.cortex import cli
from string import Template
import os

prometheus_host = os.getenv('PROMETHEUS_HOST')
prometheus_password = os.getenv('PROMETHEUS_PASSWORD')
prometheus_user = os.getenv('PROMETHEUS_USER')

def _prometheus_input(tmp_path):
    f = tmp_path / "test_integrations_prometheus_add.json"
    template = Template("""
        {
         "alias": "cortex-test",
         "host": "${prometheus_host}",
         "isDefault": true,
         "password": "${prometheus_password}",
         "prometheusTenantId": "string",
         "username": "${prometheus_user}"
        }
       """)
    content = template.substitute(prometheus_host=prometheus_host, prometheus_password=prometheus_password, prometheus_user=prometheus_user)
    f.write_text(content)
    return f

def test_integrations_prometheus_delete_all():
    cli(["integrations", "prometheus", "delete-all"])

def test_integrations_prometheus_add(tmp_path):
    f = _prometheus_input(tmp_path)
    cli(["integrations", "prometheus", "add", "-f", str(f)])

def test_integrations_prometheus_get():
    cli(["integrations", "prometheus", "get", "-a", "cortex-test"])

def test_integrations_prometheus_get_all():
    cli(["integrations", "prometheus", "get-all"])

def test_integrations_prometheus_get_default():
    cli(["integrations", "prometheus", "get-default"])

def test_integrations_prometheus_update(tmp_path):
    f = _prometheus_input(tmp_path)
    cli(["integrations", "prometheus", "update", "-a", "cortex-test", "-f", str(f)])

def test_integrations_prometheus_delete():
    cli(["integrations", "prometheus", "delete", "-a", "cortex-test"])

def test_integrations_prometheus_add_multiple(tmp_path):
    f = tmp_path / "test_integrations_prometheus_add_multiple.json"
    template = Template("""
        {
          "configurations": [
           {
            "alias": "cortex-test-2",
            "host": "${prometheus_host}",
            "isDefault": false,
            "password": "${prometheus_password}",
            "prometheusTenantId": "string",
            "username": "${prometheus_user}"
           },
           {
            "alias": "cortex-test-3",
            "host": "${prometheus_host}",
            "isDefault": false,
            "password": "${prometheus_password}",
            "prometheusTenantId": "string",
            "username": "${prometheus_user}"
           }
          ]
        }
       """)
    content = template.substitute(prometheus_host=prometheus_host, prometheus_password=prometheus_password, prometheus_user=prometheus_user)
    f.write_text(content)
    cli(["integrations", "prometheus", "add-multiple", "-f", str(f)])

def test_integrations_prometheus_delete_all():
    cli(["integrations", "prometheus", "delete-all"])

