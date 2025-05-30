from tests.helpers.utils import *

#@pytest.mark.skip(reason="Disabled until CET-15982 is resolved.")
def test():
    start_date = yesterday()
    result = cli(["audit-logs", "get", "-s", start_date])
    assert (len(result['logs']) > 0)
