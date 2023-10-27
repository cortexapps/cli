"""
Tests for aws integration commands.
"""
from cortexapps_cli.cortex import cli
import os

def test_integrations_aws_create():
    cli(["integrations", "aws", "add", "-a", "123456", "-r", "test-role"])

def test_integrations_aws_delete():
    cli(["integrations", "aws", "delete", "-a", "123456"])

def test_integrations_aws_validate_all():
    cli(["integrations", "aws", "validate-all"])

def test_integrations_aws_add():
    cli(["integrations", "aws", "add", "-a", "123456", "-r", "test-role"])

def test_integrations_aws_delete_all():
    cli(["integrations", "aws", "delete-all"])

def test_integrations_aws_update():
    cli(["integrations", "aws", "update", "-f", "tests/test_integrations_aws_config.json"])

def test_integrations_aws_get_account():
    cli(["integrations", "aws", "get", "-a", os.getenv('AWS_ACCOUNT_ID')])

def test_integrations_aws_validate_account():
    cli(["integrations", "aws", "validate", "-a", os.getenv('AWS_ACCOUNT_ID')])

def test_integrations_aws_get_all():
    cli(["integrations", "aws", "get-all"])
