"""
Tests for queries commands.
"""
from cortexapps_cli.cortex import cli
from datetime import datetime
from datetime import timedelta
import json
import pytest
from string import Template
import sys
import subprocess

def test_queries_run_json(tmp_path):
    today = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

    f = tmp_path / "cql.json"
    template = Template("""{
           "query": "tag = \\"cli-test-service\\" and custom(\\"today\\") = \\"${today}\\""
        }""")
    content = template.substitute(today=today)
    f.write_text(content)

    f1 = tmp_path / "custom-data-query-1.json"
    template = Template("""
        {
          "key": "today",
          "value": "${today}"
        }
        """)
    custom_content = template.substitute(today=today)
    f1.write_text(custom_content)

    cli(["custom-data", "add", "-t", "cli-test-service", "-f", str(f1)])
    cli(["-d", "queries", "run", "-w", "-x", "300", "-f", str(f)])

def test_queries_run_text(tmp_path):
    today = datetime.now()
    yesterday = today - timedelta(days = 1)
    yesterday = yesterday.strftime("%m-%d-%Y-%H-%M-%S")

    f = tmp_path / "cql.txt"
    template = Template("""
        tag = "cli-test-service" and custom("yesterday") = "${yesterday}"
        """)
    content = template.substitute(yesterday=yesterday)
    f.write_text(content)

    f1 = tmp_path / "custom-data-query-2.json"
    template = Template("""
        {
          "key": "yesterday",
          "value": "${yesterday}"
        }
        """)
    content = template.substitute(yesterday=yesterday)
    f1.write_text(content)

    cli(["custom-data", "add", "-t", "cli-test-service", "-f", str(f1)])
    cli(["queries", "run", "-w", "-x", "300", "-f", str(f)])

# Verify timeout handling.  If CQL query completes in 2 seconds, this test
# could fail.  Could probably put in try/catch stanza.
def test_queries_run_timeout():
    with pytest.raises(SystemExit) as excinfo:
      cli(["queries", "run", "-w", "-x", "2", "-f", "tests/test_queries.txt"])
