from tests.helpers.utils import *

def test():
    end_date = today()
    result = cli(["audit-logs", "get", "-e", end_date])
    assert (len(result['logs']) > 0)
