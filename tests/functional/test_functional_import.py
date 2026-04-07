import pytest
from tests.helpers.utils import cli, ReturnType


@pytest.mark.setup
def test():
    """Import functional test data (workflow YAMLs) into Cortex."""
    response = cli(
        ["backup", "import", "-d", "data/functional"],
        return_type=ReturnType.STDOUT,
    )
    print(response)
