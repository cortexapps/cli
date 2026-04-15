from tests.helpers.utils import *
import yaml

def test():
    cli(["workflows", "create", "-f", "data/import/workflows/cli-test-workflow.yaml"])

    response = cli(["workflows", "list"])
    assert any(workflow['tag'] == 'cli-test-workflow' for workflow in response['workflows']), "Should find workflow with tag cli-test-workflow"

    response = cli(["workflows", "get", "-t", "cli-test-workflow"])

    response = cli(["workflows", "delete", "-t", "cli-test-workflow"])

def test_run_and_get_run():
    tag = "cli-test-run-workflow"

    # Create a minimal no-action workflow that is runnable via API
    cli(["workflows", "create", "-f", "data/import/workflows/cli-test-run-workflow.yaml"])

    try:
        # Run the workflow without --wait first to get the run ID
        raw = cli(["workflows", "run", "-t", tag], return_type=ReturnType.RAW)
        assert raw.exit_code == 0, f"run failed (exit {raw.exit_code}): {raw.stdout}"
        run_response = json.loads(raw.stdout)
        run_id = run_response["id"]

        # Poll with get-run until completed (or timeout after 30s)
        import time
        deadline = time.time() + 30
        status = None
        while time.time() < deadline:
            get_response = cli(["workflows", "get-run", "-t", tag, "-r", run_id])
            status = get_response.get("status")
            if status in ("COMPLETED", "FAILED", "CANCELLED"):
                break
            time.sleep(2)

        assert status == "COMPLETED", f"Expected COMPLETED, got {status}"
        assert get_response["id"] == run_id
    finally:
        # Clean up
        cli(["workflows", "delete", "-t", tag])
