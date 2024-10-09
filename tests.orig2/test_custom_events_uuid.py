from common import *

def test(capsys):
    response = cli_command(capsys, ["custom-events", "create", "-t", "warehousing", "-f", "data/run-time/custom-events-configure.json"])
    uuid = response['uuid']

    cli_command(capsys, ["custom-events", "get-by-uuid", "-t", "warehousing", "-u", uuid])
    assert response['type'] == "CONFIG_SERVICE"

    cli(["-q", "custom-events", "update-by-uuid", "-t", "warehousing", "-u", uuid, "-f", "data/run-time/custom-events.json"])
    capsys.readouterr()

    response = cli_command(capsys, ["custom-events", "get-by-uuid", "-t", "warehousing", "-u", uuid])
    assert response['type'] == "VALIDATE_SERVICE"

    cli(["-q", "custom-events", "delete-by-uuid", "-t", "warehousing", "-u", uuid])

    # Custom event was deleted, so verify it cannot be retrieved.
    with pytest.raises(SystemExit) as excinfo:
       cli(["-q", "custom-events", "get-by-uuid", "-t", "warehousing", "-u", uuid])
       out, err = capsys.readouterr()

       assert out == "Bad Request"
       assert excinfo.value.code == 144

    cli(["-q", "custom-events", "delete-all", "-t", "warehousing"])
