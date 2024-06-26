"""
Tests for pagerduty integration commands.
"""
from cortexapps_cli.cortex import cli
from string import Template
import os

pagerduty_token = os.getenv('PAGERDUTY_TOKEN')

def test_integrations_pagerduty(tmp_path):
    f = tmp_path / "test_integrations_pagerduty_add.json"
    template = Template("""
         {
          "isTokenReadonly": true,
          "token": "${pagerduty_token}"
         }
       """)
    content = template.substitute(pagerduty_token=pagerduty_token)
    f.write_text(content)

    cli(["integrations", "pagerduty", "delete"])
    cli(["integrations", "pagerduty", "add", "-f", str(f)])
    cli(["integrations", "pagerduty", "get"])
    cli(["integrations", "pagerduty", "validate"])
    cli(["integrations", "pagerduty", "delete"])

