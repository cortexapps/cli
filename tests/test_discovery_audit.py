"""
Tests for the discovery-audit commands.
"""
from cortexapps_cli.cortex import cli

def test_discovery_audit_get():
    cli(["discovery-audit", "get"])

def test_discovery_audit_get_include_ignored():
    cli(["discovery-audit", "get", "-i"])

def test_discovery_audit_filter_on_source():
    cli(["discovery-audit", "get", "-s", "GITHUB"])

def test_discovery_audit_filter_on_type():
    cli(["discovery-audit", "get", "-t", "NEW_REPOSITORY"])

