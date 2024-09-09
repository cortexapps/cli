from common import *
from cortex_github import *

# I don't think these tests can reliably run in parallel.  Can result in PyGitHub reporting errors like this:
# FAILED tests/test_github_cortex_yaml_in_root.py::test
# github.GithubException.GithubException: 409 {"message": "is at ef660f9 but expected 418d7ec", "documentation_url":
@pytest.mark.skipif(enable_ui_editing("SERVICE") == True, reason="Account flag ENABLE_UI_EDITING for SERVICE is true.")
@pytest.mark.skipif(os.getenv('CORTEX_ENV') != "staging" or os.getenv('CORTEX_TENANT') != "jeff-sandbox", reason="To prevent git commit clashes, the test for cortex.yaml in the root will only run for main API test in staging")
def test_github_cortex_yaml_in_root(capsys):
    assert gitops_add(capsys, "data/run-time/gitops.tmpl", "cortex.yaml") == True, "failed to find commit in gitops-logs"

    response = cli_command(capsys, ["catalog", "details", "-t", "gitops-entity"])
    assert response['tag'] == "gitops-entity", "Entity details can be retrieved for gitops entity"

@pytest.mark.skipif(enable_ui_editing("SERVICE") == True, reason="Account flag ENABLE_UI_EDITING for SERVICE is true.")
def test_github_entity_in_dot_cortex(capsys):
    assert gitops_add(capsys, "data/run-time/gitops-catalog.tmpl", ".cortex/catalog/" + os.getenv('CORTEX_ENV') + "-" + os.getenv('CORTEX_TENANT') + "-gitops-catalog.yaml") == True, "failed to find commit in gitops-logs"
    response = cli_command(capsys, ["catalog", "details", "-t", os.getenv('CORTEX_ENV') + "-" + os.getenv('CORTEX_TENANT') + "-gitops-catalog"])
    assert response['tag'] == os.getenv('CORTEX_ENV') + "-" + os.getenv('CORTEX_TENANT') + "-gitops-catalog"
