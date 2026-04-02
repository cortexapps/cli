from tests.helpers.utils import *

@pytest.mark.skip(reason="Disabled until CET-24479 is resolved.")
def test():
    response = cli(["catalog", "list", "-o", "cli-test-team-1,cli-test-team-2"])
    assert (response['total'] == 2)
