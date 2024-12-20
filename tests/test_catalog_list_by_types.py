from tests.helpers.utils import *

def test():
    response = cli(["catalog", "list", "-g", "public-api-test", "-t", "component"])
    assert response['total'] > 0, "Should find at least 1 entity of type 'component'"
