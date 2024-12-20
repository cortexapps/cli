from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/unarchive-entity.yaml"])
    cli(["catalog", "archive", "-t", "unarchive-entity"])

    response = cli(["catalog", "details", "-t", "unarchive-entity"])
    assert response['isArchived'] == True, "isArchived attribute should be true"

    response = cli(["catalog", "unarchive", "-t", "unarchive-entity"])
    assert response['isArchived'] == False, "isArchived attribute should not be true"
