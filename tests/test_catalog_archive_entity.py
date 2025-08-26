from tests.helpers.utils import *

def test():
    cli(["catalog", "archive", "-t", "cli-test-archive-entity"])

    response = cli(["catalog", "details", "-t", "cli-test-archive-entity"])
    assert response['isArchived'] == True, "isArchived attribute should be true"
