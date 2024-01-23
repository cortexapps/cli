"""
Tests for scorecards commands.
"""
from cortexapps_cli.cortex import cli

def test_scorecards():
    cli(["scorecards", "create", "-f", "tests/test_scorecards.yaml"])

    cli(["scorecards", "list"])

    cli(["scorecards", "shield", "-s", "test-scorecard", "-t", "test-service"])

    cli(["scorecards", "get", "-t", "test-scorecard"])

    cli(["scorecards", "descriptor", "-t", "test-scorecard"])

    cli(["scorecards", "next-steps", "-t", "test-scorecard", "-e", "test-service"])

    # Not sure if we can run this cli right away.  Newly-created Scorecard might not be evaluated yet.
    cli(["scorecards", "scores", "-t", "test-scorecard", "-e", "test-service"])

    cli(["scorecards", "scores", "-t", "test-scorecard"])
