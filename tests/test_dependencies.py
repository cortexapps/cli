from tests.helpers.utils import *

def test():
    callerTag = "fraud-analyzer"
    calleeTag = "backend-worker"

    cli(["dependencies", "delete-all", "-r", callerTag])

    cli(["dependencies", "add-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])

    cli(["dependencies", "create", "-r", callerTag, "-e", calleeTag, "-m", "GET", "-p", "/api/v1/audit-logs"])
    cli(["dependencies", "update", "-r", callerTag, "-e", calleeTag, "-m", "GET", "-p", "/api/v1/audit-logs", "-f", "data/run-time/dependencies-update.json"])
    result = cli(["dependencies", "get", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/github/configurations"])
    assert result["callerTag"] == callerTag, "callerTag should be " + callerTag
    assert result["calleeTag"] == calleeTag, "calleeTag should be " + calleeTag

    cli(["dependencies", "get", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/github/configurations"])

    result = cli(["dependencies", "get-all", "-r", "fraud-analyzer", "-o"])
    assert any(dependency['callerTag'] == callerTag and dependency['path'] == "/api/v1/github/configurations" for dependency in result["dependencies"])

    cli(["dependencies", "delete", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/audit-logs"])
    cli(["dependencies", "add-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])
    cli(["dependencies", "delete-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])
    cli(["dependencies", "delete-all", "-r", "fraud-analyzer"])
