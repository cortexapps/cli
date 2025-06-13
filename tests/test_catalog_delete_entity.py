from tests.helpers.utils import *

def test():
    response = cli(["catalog", "details", "-t", "cli-test-delete-entity"])
    assert response['tag'] == 'cli-test-delete-entity', "Should find newly created entity"

    cli(["catalog", "delete", "-t", "cli-test-delete-entity"])

    # Since entity is deleted, cli command should exit with a Not Found, 404 error.
    response = cli(["catalog", "details", "-t", "cli-test-delete-entity"], ReturnType.RAW)

    assert "HTTP Error 404:" in response.stdout, "command fails with 403 error"
