from tests.helpers.utils import *

def test():
    end_date = today()
    start_date = yesterday()
    response = json_response(["audit-logs", "get", "-s", start_date, "-e", end_date])
    assert (len(response['logs']) > 0)
