from tests.helpers.utils import *

def test():
    end_date = today()
    response = json_response(["audit-logs", "get", "-e", end_date])
    assert (len(response['logs']) > 0)
