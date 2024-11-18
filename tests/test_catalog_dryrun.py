from common import *

def test(capsys):
    cli(["-q", "catalog", "create", "-f", "data/run-time/create-dryrun.yaml", "--dryRun"])
    # Need to clear captured system output from the above commands to clear the way for the next one.
    capsys.readouterr()

    # Entity should not exist.
    with pytest.raises(SystemExit) as excinfo:
       cli(["catalog", "descriptor", "-t", "create-entity-dryrun"])
       out, err = capsys.readouterr()

       assert out == "Not Found"
       assert excinfo.value.code == 404
