from common import *
from cortex_github import *

# I don't think these tests can reliably run in parallel.  Can result in PyGitHub reporting errors like this:
# FAILED tests/test_github_cortex_yaml_in_root.py::test
# github.GithubException.GithubException: 409 {"message": "is at ef660f9 but expected 418d7ec", "documentation_url":
@pytest.mark.skipif(enable_ui_editing("SERVICE") == True, reason="Account flag ENABLE_UI_EDITING for SERVICE is true.")
def test_github_cortex_yaml_in_root(capsys):
    assert gitops_add(capsys, "data/run-time/gitops.tmpl", "cortex.yaml") == True, "failed to find commit in gitops-logs"

    response = cli_command(capsys, ["catalog", "details", "-t", "gitops-entity"])
    assert response['tag'] == "gitops-entity", "Entity details can be retrieved for gitops entity"

@pytest.mark.skipif(enable_ui_editing("SERVICE") == True, reason="Account flag ENABLE_UI_EDITING for SERVICE is true.")
def test_github_entity_in_dot_cortex(capsys):
    assert gitops_add(capsys, "data/run-time/gitops2.tmpl", ".cortex/catalog/gitops2.yaml") == True, "failed to find commit in gitops-logs"
    response = cli_command(capsys, ["catalog", "details", "-t", "gitops2"])
    assert response['tag'] == "gitops2"
