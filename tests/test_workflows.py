from tests.helpers.utils import *
import yaml

def test():
    cli(["workflows", "create", "-f", "data/run-time/test-workflows.json"])

    response = cli(["workflows", "list"])
    assert any(workflow['tag'] == 'hello-world' for workflow in response['workflows']), "Should find workflow with tag hello-world"

    response = cli(["workflows", "get", "-t", "hello-world"])

    response = cli(["workflows", "delete", "-t", "hello-world"])
