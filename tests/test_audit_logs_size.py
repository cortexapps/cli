from tests.helpers.utils import *

#@pytest.mark.skip(reason="Disabled until CET-15982 is resolved.")
def test():
    result = cli(["audit-logs", "get", "-p", "0", "-z", "1"])
    assert (len(result['logs']) == 1)