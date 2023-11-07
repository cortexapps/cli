"""
Tests for scorecards commands.
"""
from cortexapps_cli.cortex import cli

def test_scorecards_create():
    cli(["scorecards", "create", "-f", "tests/test_scorecards.yaml"])

def test_scorecards_list():
    cli(["scorecards", "list"])

def test_scorecards_shield():
    cli(["scorecards", "shield", "-s", "test-scorecard", "-t", "cli-service"])

def test_scorecards_get():
    cli(["scorecards", "get", "-t", "test-scorecard"])

def test_scorecards_descriptor():
    cli(["scorecards", "descriptor", "-t", "test-scorecard"])

def test_scorecards_next_steps():
    cli(["scorecards", "next-steps", "-t", "test-scorecard", "-e", "test-service"])

def test_scorecards_scores():
    # Not sure if we can run this cli right away.  Newly-created Scorecard might not be evaluated yet.
    cli(["scorecards", "scores", "-t", "test-scorecard", "-e", "test-service"])
