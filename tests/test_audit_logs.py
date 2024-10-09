from tests.helpers.utils import *

def test():
    result = cli(["audit-logs", "get"])
    assert (len(result['logs']) > 0)
