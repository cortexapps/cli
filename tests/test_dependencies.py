from tests.helpers.utils import *

def test():
    callerTag = "fraud-analyzer"
    calleeTag = "backend-worker"

    cli(["dependencies", "delete-all", "-r", callerTag])

    cli(["dependencies", "add-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])

    cli(["dependencies", "add", "-r", callerTag, "-e",
         calleeTag, "-m", "GET", "-p", "/api/v1/audit-logs", "-f", "data/run-time/dependencies.json"])
    cli(["dependencies", "update", "-r", callerTag, "-e", calleeTag, "-m", "GET", "-p", "/api/v1/audit-logs", "-f", "data/run-time/dependencies-update.json"])
    response = json_response(["dependencies", "get", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/github/configurations"])
    assert response["callerTag"] == callerTag, "callerTag should be " + callerTag
    assert response["calleeTag"] == calleeTag, "calleeTag should be " + calleeTag

    cli(["dependencies", "get", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/github/configurations"])

    response = json_response(["dependencies", "get-all", "-r", "fraud-analyzer", "-o"])
    assert any(dependency['callerTag'] == callerTag and dependency['path'] == "/api/v1/github/configurations" for dependency in response["dependencies"])

    cli(["dependencies", "delete", "-r", "fraud-analyzer", "-e", "backend-worker", "-m", "GET", "-p", "/api/v1/audit-logs"])
    cli(["dependencies", "add-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])
    cli(["dependencies", "delete-in-bulk", "-f", "data/run-time/dependencies-bulk.json"])
    cli(["dependencies", "delete-all", "-r", "fraud-analyzer"])
