import pytest
from unittest.mock import patch, MagicMock, ANY
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
    mock_run.assert_called_once_with("github-actions-deploy", solutions_dir=None, ctx=ANY, no_prompt=False)


def test_install_skip_post_install_setup_flag_skips_script():
    """--skip-post-install-setup prints 'Run setup later' and does NOT call the script."""
    with patch("cortexapps_cli.commands.solutions._has_post_install", return_value=True), \
         patch("cortexapps_cli.commands.solutions._run_post_install_script") as mock_run, \
         patch("cortexapps_cli.commands.solutions._build_client", return_value=MagicMock()), \
         patch("cortexapps_cli.commands.backup.import_tenant"):
        result = runner.invoke(
            app,
            ["-k", "fake", "solutions", "install", "-s", "github-actions-deploy",
             "--skip-post-install-setup", "--no-prompt"],
        )
    assert "Run setup later with: cortex solutions post-install -s github-actions-deploy" in result.output
    mock_run.assert_not_called()


def test_install_prompts_and_runs_post_install_on_yes():
    """Without --skip-post-install-setup, answering 'y' at the prompt calls the script."""
    with patch("cortexapps_cli.commands.solutions._has_post_install", return_value=True), \
         patch("cortexapps_cli.commands.solutions._run_post_install_script") as mock_run, \
         patch("cortexapps_cli.commands.solutions._build_client", return_value=MagicMock()), \
         patch("cortexapps_cli.commands.backup.import_tenant"), \
         patch("cortexapps_cli.commands.solutions._post_install_menu"):
        result = runner.invoke(
            app,
            ["-k", "fake", "solutions", "install", "-s", "github-actions-deploy"],
            input="y\n",
        )
    assert "This solution includes a post-install setup script" in result.output
    mock_run.assert_called_once_with("github-actions-deploy", solutions_dir=None, ctx=ANY)
