"""
Tests for the gitops-logs commands.
"""
from cortexapps_cli.cortex import cli
from datetime import datetime, timedelta, timezone
import json
import sys
import pytest

def test_gitops_logs_get():
    cli(["gitops-logs", "get"])

def test_gitops_logs_page_size(capsys):
    cli(["-d", "gitops-logs", "get", "-p", "1", "-z", "5"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert len(out['logs']) == 5, "Changing page size should return requested amount of entries"
