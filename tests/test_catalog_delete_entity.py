from common import *

def test(capsys):
    cli_command(capsys, ["catalog", "create", "-f", "data/run-time/delete-entity.yaml"])
    response = cli_command(capsys, ["catalog", "details", "-t", "delete-entity"])
    assert response['tag'] == 'delete-entity', "Should find newly created entity"

    cli(["-q", "catalog", "delete", "-t", "delete-entity"])

    # Since entity is deleted, cli command should exit with a Not Found, 404 error.
    with pytest.raises(SystemExit) as excinfo:
       cli(["catalog", "details", "-t", "delete-entity"])
       out, err = capsys.readouterr()

       assert out == "Not Found"
       assert excinfo.value.code == 404
