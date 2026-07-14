from tests.helpers.utils import cli, ReturnType


def test_solutions_help():
    result = cli(["solutions", "--help"], return_type=ReturnType.RAW)
    assert result.exit_code == 0
    assert "solutions" in result.output.lower()


def test_solutions_list_shows_tag():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "github-starter" in result.output


def test_solutions_list_shows_name():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "GitHub Starter" in result.output


def test_solutions_list_shows_description():
    result = cli(["solutions", "list"], return_type=ReturnType.RAW)
    assert result.exit_code == 0, result.output
    assert "GitHub-integrated" in result.output
