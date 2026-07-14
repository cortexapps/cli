from tests.helpers.utils import cli, ReturnType


def test_solutions_help():
    result = cli(["solutions", "--help"], return_type=ReturnType.RAW)
    assert result.exit_code == 0
    assert "solutions" in result.output.lower()
