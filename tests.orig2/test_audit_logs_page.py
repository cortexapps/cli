from tests.helpers.utils import *

def test():
    response = json_response(["audit-logs", "get", "-p", "0"])
    assert (len(response['logs']) > 0)