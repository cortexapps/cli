from tests.helpers.utils import *

# This just ensures getting all logs does not fail.  Could probably get rid of this test.
def test_gitops_logs_get():
    cli(["gitops-logs", "get"])

def test_gitops_logs_page_size(capsys):
    response = cli(["gitops-logs", "get", "-p", "1", "-z", "5"])
    assert len(response['logs']) == 5, "Changing page size should return requested amount of entries"
