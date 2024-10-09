from tests.helpers.utils import *

def test():
    result = cli(["audit-logs", "get", "-p", "0"])
    assert (len(result['logs']) > 0)
