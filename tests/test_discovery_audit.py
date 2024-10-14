from tests.helpers.utils import *

def test_discovery_audit_get():
    result = cli(["discovery-audit", "get"])

def test_discovery_audit_get_include_ignored():
    result = cli(["discovery-audit", "get", "-ii"])

def test_discovery_audit_filter_on_source():
    result = cli(["discovery-audit", "get", "-s", "GITHUB"])

def test_discovery_audit_filter_on_type():
    result = cli(["discovery-audit", "get", "-ty", "NEW_REPOSITORY"])

