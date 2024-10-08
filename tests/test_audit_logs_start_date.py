from tests.helpers.utils import *

def test():
    start_date = yesterday()
    response = json_response(["audit-logs", "get", "-s", start_date])
    assert (len(response['logs']) > 0)
