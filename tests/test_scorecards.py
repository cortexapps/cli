"""
Tests for scorecards commands.
"""
from cortexapps_cli.cortex import cli
import json

def test_scorecards():
    cli(["scorecards", "create", "-f", "tests/test_scorecards.yaml"])

    cli(["scorecards", "list"])

    cli(["scorecards", "shield", "-s", "test-scorecard", "-t", "test-service"])

    cli(["scorecards", "get", "-t", "test-scorecard"])

    cli(["scorecards", "descriptor", "-t", "test-scorecard"])

    cli(["scorecards", "next-steps", "-t", "test-scorecard", "-e", "test-service"])

    # Not sure if we can run this cli right away.  Newly-created Scorecard might not be evaluated yet.
    # 2024-05-06, additionally now blocked by CET-8882
    # cli(["scorecards", "scores", "-t", "test-scorecard", "-e", "test-service"])

    cli(["scorecards", "scores", "-t", "test-scorecard"])

def test_scorecards_drafts(capsys):
    cli(["scorecards", "create", "-f", "tests/test_scorecards_draft.yaml"])
    # Only capturing this so it doesn't show up in next call to capsys.
    out, err = capsys.readouterr()

    cli(["scorecards", "list", "-s"])
    out, err = capsys.readouterr()

    out = json.loads(out)
    assert any(scorecard['tag'] == 'test-scorecard-draft' for scorecard in out['scorecards'])
