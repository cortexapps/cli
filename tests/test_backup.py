"""
Tests for backup commands.
"""
from cortexapps_cli.cortex import cli

import pytest

def test_export():
    cli(["-t", "rich-sandbox", "backup", "export"])
    global output_behavior
    output_behavior="print"
