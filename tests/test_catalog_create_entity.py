from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/create-entity.yaml"])

    response = cli(["catalog", "descriptor", "-t", "create-entity"])
    assert response['info']['x-cortex-tag'] == "create-entity"
