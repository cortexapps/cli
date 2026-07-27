import os
from unittest.mock import patch
from tests.helpers.utils import cli, ReturnType


def test_solutions_help():
    result = cli(["solutions", "--help"], return_type=ReturnType.RAW)
    assert result.exit_code == 0
    assert "solutions" in result.output.lower()


def test_solutions_list_shows_tag():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "environments" in result.output


def test_solutions_list_shows_name():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "Environments" in result.output


def test_solutions_list_shows_description():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "CVE" in result.output


def test_solutions_list_custom_dir():
    import os
    test_dir = os.path.join(os.path.dirname(__file__), "solutions")
    result = cli(["solutions", "--solutions-dir", test_dir, "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "github-starter" in result.output


def test_solutions_info_known_tag():
    result = cli(["solutions", "info", "-s", "environments"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "environment" in result.output


def test_solutions_info_custom_dir():
    import os
    test_dir = os.path.join(os.path.dirname(__file__), "solutions")
    result = cli(["solutions", "--solutions-dir", test_dir, "info", "-s", "github-starter"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "GitHub Starter" in result.output


def test_solutions_info_unknown_tag():
    result = cli(["solutions", "info", "-s", "nonexistent-xyz-abc"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_solutions_install_unknown_tag():
    # Unknown-tag check runs before auth check, so no credentials needed
    result = cli(["solutions", "install", "-s", "nonexistent-xyz-abc"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_solutions_install_no_auth():
    # Known tag, but no credentials — should fail with auth error.
    # Control the credential environment directly so this test runs everywhere.
    with patch.dict(os.environ, {"CORTEX_API_KEY": ""}):
        result = cli(["--config", "/nonexistent/path", "solutions", "install", "-s", "environments"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "authentication required" in result.output.lower()


def test_solutions_uninstall_unknown_tag():
    # Unknown-tag check runs before auth check, so no credentials needed
    result = cli(["solutions", "uninstall", "-s", "nonexistent-xyz-abc"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_solutions_uninstall_no_auth():
    # Known tag, but no credentials — should fail with auth error.
    # Control the credential environment directly so this test runs everywhere.
    with patch.dict(os.environ, {"CORTEX_API_KEY": ""}):
        result = cli(["--config", "/nonexistent/path", "solutions", "uninstall", "-s", "environments"], return_type=ReturnType.RAW)
    assert result.exit_code == 1
    assert "authentication required" in result.output.lower()
