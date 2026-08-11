import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from cortexapps_cli.cli import app

runner = CliRunner()


def test_post_install_no_setup_for_ai_agents():
    result = runner.invoke(app, ["solutions", "post-install", "-s", "ai-agents"])
    assert result.exit_code == 0
    assert "No post-install setup available" in result.output


def test_post_install_unknown_solution():
    result = runner.invoke(app, ["solutions", "post-install", "-s", "nonexistent-xyz"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_post_install_calls_run_for_github_actions():
    with patch("cortexapps_cli.commands.solutions._run_post_install_script") as mock_run:
        runner.invoke(app, ["solutions", "post-install", "-s", "github-actions-deploy"])
    mock_run.assert_called_once_with("github-actions-deploy", solutions_dir=None)
