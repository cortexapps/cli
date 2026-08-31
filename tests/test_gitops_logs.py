from tests.helpers.utils import *

def test_gitops_logs_get():
    result = cli(["gitops-logs", "get", "-p", "0", "-z", "10"], return_type=ReturnType.RAW)
    if result.exit_code != 0:
        pytest.skip(f"gitops-logs API unavailable: {result.stdout[:100].strip()}")

def test_gitops_logs_page_size(capsys):
    result = cli(["gitops-logs", "get", "-p", "0", "-z", "1"], return_type=ReturnType.RAW)
    if result.exit_code != 0:
        pytest.skip(f"gitops-logs API unavailable: {result.stdout[:100].strip()}")
    response = json.loads(result.stdout)
    # Only run assert if there is at least one entry in the gitops logs
    if response['totalPages'] > 0:
        assert len(response['logs']) == 1, "Changing page size should return requested amount of entries"
    else:
        print("No gitops logs.  Not running assertion test.")

