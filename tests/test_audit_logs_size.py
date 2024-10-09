from tests.helpers.utils import *

def test():
    result = cli(["audit-logs", "get", "-p", "0", "-z", "1"])
    assert (len(result['logs']) == 1)
