from tests.helpers.utils import *

def test(capsys):
    response = cli(["catalog", "create", "-f", "data/run-time/archive-entity.yaml"])
    response = cli(["catalog", "archive", "-t", "archive-entity"])

    response = cli(["catalog", "list", "-g", "cli-test", "-z", "500"])
    assert not any(entity['tag'] == 'archive-entity' for entity in response['entities']), "Should not find archived entity"

    response = cli(["catalog", "list", "-g", "cli-test", "-a", "-z", "500"])
    assert any(entity['tag'] == 'archive-entity' for entity in response['entities']), "Should find archived entity"
