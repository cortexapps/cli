from tests.helpers.utils import *

@pytest.mark.skip(reason="Disabled until CET-15982 is resolved.")
def test():
    end_date = today()
    result = cli(["audit-logs", "get", "-e", end_date])
    assert (len(result['logs']) > 0)
