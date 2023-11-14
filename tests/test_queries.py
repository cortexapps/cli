"""
Tests for queries commands.
"""
from cortexapps_cli.cortex import cli
import json
import pytest

def test_queries_run_json():
    cli(["queries", "run", "-w", "-f", "tests/test_queries.json"])

def test_queries_run_text():
    cli(["queries", "run", "-w", "-f", "tests/test_queries.txt"])

# Verify timeout handling.  If CQL query completes in 2 seconds, this test
# could fail.  Could probably put in try/catch stanza.
def test_queries_run_timeout():
    with pytest.raises(SystemExit) as excinfo:
      cli(["queries", "run", "-w", "-x", "2", "-f", "tests/test_queries.txt"])
