from common import *

def test(capsys):
    cli_command(capsys, ["catalog", "create", "-f", "data/run-time/docs-entity.yaml"])

    cli_command(capsys, ["docs", "update", "-t", "docs-entity", "-f", "data/run-time/docs.yaml"])

    response = cli_command(capsys, ["docs", "get", "-t", "docs-entity"])
    spec = yaml.safe_load(response['spec'])
    assert spec['info']['title'] == "Simple API overview", "API spec should have been retrieved"

    cli_command(capsys, ["-q", "docs", "delete", "-t", "docs-entity"], "none")
    with pytest.raises(SystemExit) as excinfo:
       cli(["-q", "docs", "get", "-t", "docs-entity"])
       out, err = capsys.readouterr()

       assert out == "Not Found"
       assert excinfo.value.code == 404
