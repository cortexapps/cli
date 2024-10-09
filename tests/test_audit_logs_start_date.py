from tests.helpers.utils import *

def test():
    start_date = yesterday()
    result = cli(["audit-logs", "get", "-s", start_date])
    assert (len(result['logs']) > 0)
