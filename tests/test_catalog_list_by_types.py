from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "list", "-g", "public-api-test", "-t", "component"])
    assert response['total'] > 0, "Should find at least 1 entity of type 'component'"
