"""
Tests for aws integration commands.
"""
from cortexapps_cli.cortex import cli
import os

def test_integrations_aws_create():
    cli(["integrations", "aws", "add", "-a", "123456", "-r", "test-role"])

    cli(["integrations", "aws", "delete", "-a", "123456"])

    cli(["integrations", "aws", "validate-all"])

    cli(["integrations", "aws", "add", "-a", "123456", "-r", "test-role"])

    cli(["integrations", "aws", "delete-all"])

    cli(["integrations", "aws", "update", "-f", "tests/test_integrations_aws_config.json"])

    cli(["integrations", "aws", "get", "-a", os.getenv('AWS_ACCOUNT_ID')])

    cli(["integrations", "aws", "validate", "-a", os.getenv('AWS_ACCOUNT_ID')])

    cli(["integrations", "aws", "get-all"])
