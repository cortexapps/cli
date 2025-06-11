from tests.helpers.utils import *

def test():
    cli(["catalog", "archive", "-t", "cli-test-unarchive-entity"])

    response = cli(["catalog", "details", "-t", "cli-test-unarchive-entity"])
    assert response['isArchived'] == True, "isArchived attribute should be true"

    response = cli(["catalog", "unarchive", "-t", "cli-test-unarchive-entity"])
    assert response['isArchived'] == False, "isArchived attribute should not be true"
