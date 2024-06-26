from common import *

def test(capsys):
    callerTag = "fraud-analyzer"
    calleeTag = "backend-worker"

    cli(["-q", "dependencies", "delete-all", "-r", callerTag])

    cli_command(capsys, ["dependencies", "add-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])

    cli_command(capsys, ["dependencies", "add", "-r", callerTag, "-e",
          calleeTag, "-m", "GET", "-p", "/api/v1/audit-logs", "-f", "data/run-time/dependencies.json"])
    cli_command, (["dependencies", "update", "-r", callerTag, "-e", calleeTag, "-m", "GET", "-p", "/api/v1/audit-logs", "-f", "data/run-time/dependencies-update.json"])
    response = cli_command(capsys, ["dependencies", "get", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/github/configurations"])
    assert response["callerTag"] == callerTag, "callerTag should be " + callerTag
    assert response["calleeTag"] == calleeTag, "calleeTag should be " + calleeTag

    cli_command(capsys, ["dependencies", "get", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/github/configurations"])

    response = cli_command(capsys, ["dependencies", "get-all", "-r", "fraud-analyzer", "-o"])
    assert any(dependency['callerTag'] == callerTag and dependency['path'] == "/api/v1/github/configurations" for dependency in response["dependencies"])

    cli(["-q", "dependencies", "delete", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/audit-logs"])
    cli(["-q", "dependencies", "add-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])
    cli(["-q", "dependencies", "delete-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])
    cli(["-q", "dependencies", "delete-all", "-r", "fraud-analyzer"])
