"""
Tests for the audit-logs commands.
"""
from cortexapps_cli.cortex import cli
from datetime import datetime, timedelta, timezone
import json
import sys
import pytest

def test_audit_logs_get():
    cli(["audit-logs", "get"])

def test_audit_logs_page_size(capsys):
    cli(["audit-logs", "get", "-p", "1", "-z", "5"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert len(out['logs']) == 5, "Changing page size should return requested amount of entries"

def test_audit_logs_with_start_and_end(capsys):
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    cli(["audit-logs", "get", "-e", now.isoformat(), "-s", yesterday.isoformat()])

def test_audit_logs_with_start():
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    cli(["audit-logs", "get", "-s", yesterday.isoformat()])

def test_audit_logs_with_end():
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    cli(["audit-logs", "get", "-e", yesterday.isoformat()])
