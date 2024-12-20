from tests.helpers.utils import *

def test(capsys):
    response = cli(["catalog", "list", "-g", "public-api-test", "-z", "500"])
    assert not any(entity['tag'] == 'robot-item-sorter' for entity in response['entities']), "Should not find archived entity"

    response = cli(["catalog", "list", "-g", "public-api-test", "-a", "-z", "500"])
    assert any(entity['tag'] == 'robot-item-sorter' for entity in response['entities']), "Should find archived entity"
