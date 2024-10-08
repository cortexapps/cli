from tests.helpers.utils import *

def test():
    response = json_response(["audit-logs", "get"])
    assert (len(response['logs']) > 0)
