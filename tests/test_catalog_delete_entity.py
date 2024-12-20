from tests.helpers.utils import *

def test():
    cli(["catalog", "create", "-f", "data/run-time/delete-entity.yaml"])
    response = cli(["catalog", "details", "-t", "delete-entity"])
    assert response['tag'] == 'delete-entity', "Should find newly created entity"

    cli(["catalog", "delete", "-t", "delete-entity"])

    # Since entity is deleted, cli command should exit with a Not Found, 404 error.
    response = cli(["catalog", "details", "-t", "delete-entity"], ReturnType.RAW)

    assert "HTTP Error 404:" in response.stdout, "command fails with 403 error"
