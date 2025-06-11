from tests.helpers.utils import *

def test_gitops_logs_get():
    cli(["gitops-logs", "get"])

def test_gitops_logs_page_size(capsys):
    response = cli(["gitops-logs", "get", "-p", "0", "-z", "1"])
    # Only run assert if there is at least one entry in the gitops logs
    if response['totalPages'] > 0:
        assert len(response['logs']) == 1, "Changing page size should return requested amount of entries"
    else:
        print("No gitops logs.  Not running assertion test.")

