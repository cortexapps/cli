from tests.helpers.utils import *

def test():
    cli(["catalog", "archive", "-t", "archive-entity"])

    response = cli(["catalog", "details", "-t", "archive-entity"])
    assert response['isArchived'] == True, "isArchived attribute should be true"
