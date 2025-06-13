from tests.helpers.utils import *
import yaml

def test():
    cli(["workflows", "create", "-f", "data/import/workflows/cli-test-workflow.yaml"])

    response = cli(["workflows", "list"])
    assert any(workflow['tag'] == 'cli-test-workflow' for workflow in response['workflows']), "Should find workflow with tag cli-test-workflow"

    response = cli(["workflows", "get", "-t", "cli-test-workflow"])

    response = cli(["workflows", "delete", "-t", "cli-test-workflow"])
