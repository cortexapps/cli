import json
import os
import subprocess
import time

from helpers.utils import cli, ReturnType

RESOURCE_PREFIX = "cli-functional-test-"


def get_env(name):
    """Get a required environment variable or raise."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value


def gh_api(method, path, input_data=None):
    """Call the GitHub API via the gh CLI.

    Returns parsed JSON response. Raises on non-zero exit code.
    """
    pat = get_env("GITHUB_TOKEN")
    cmd = ["gh", "api", "-X", method, path, "-H", "Accept: application/vnd.github+json"]

    env = {**os.environ, "GH_TOKEN": pat}

    if input_data is not None:
        cmd.extend(["--input", "-"])
        result = subprocess.run(
            cmd,
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            env=env,
        )
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

    if result.returncode != 0:
        raise RuntimeError(f"gh api {method} {path} failed: {result.stderr}")

    if not result.stdout.strip():
        return None

    return json.loads(result.stdout)


def safe_delete_repo(repo_full_name):
    """Delete a GitHub repo, but only if the name matches the safety prefix."""
    repo_name = repo_full_name.split("/")[-1]
    if not repo_name.startswith(RESOURCE_PREFIX):
        raise RuntimeError(
            f"Refusing to delete repo '{repo_full_name}' — "
            f"name does not start with '{RESOURCE_PREFIX}'"
        )
    pat = get_env("GITHUB_TOKEN")
    env = {**os.environ, "GH_TOKEN": pat}
    subprocess.run(
        ["gh", "repo", "delete", repo_full_name, "--yes"],
        capture_output=True,
        text=True,
        env=env,
    )


def safe_delete_team(org, team_slug):
    """Delete a GitHub team, but only if the slug matches the safety prefix."""
    if not team_slug.startswith(RESOURCE_PREFIX):
        raise RuntimeError(
            f"Refusing to delete team '{team_slug}' — "
            f"name does not start with '{RESOURCE_PREFIX}'"
        )
    gh_api("DELETE", f"/orgs/{org}/teams/{team_slug}")


def validate_test_org(org):
    """Verify the org has the cortex-cli-functional-test safety marker.

    Checks for a custom property 'cortex-cli-functional-test' set to 'true'.
    Raises RuntimeError if not found.
    """
    try:
        props = gh_api("GET", f"/orgs/{org}/properties/values")
    except RuntimeError:
        raise RuntimeError(
            f"Cannot read custom properties for org '{org}'. "
            f"Ensure GITHUB_TOKEN has admin:org scope."
        )

    try:
        org_props = gh_api("GET", f"/orgs/{org}/properties/schema")
    except RuntimeError:
        org_props = []

    found = False
    if isinstance(org_props, list):
        for prop in org_props:
            if prop.get("property_name") == "cortex-cli-functional-test":
                found = True
                break

    if not found:
        raise RuntimeError(
            f"Org '{org}' does not have custom property 'cortex-cli-functional-test'. "
            f"This safety check prevents accidental use of production orgs. "
            f"Create this custom property in your test org's settings."
        )


def create_test_repo(org, repo_name):
    """Create a test repo with README and safety custom property."""
    full_name = f"{org}/{repo_name}"
    gh_api("POST", f"/orgs/{org}/repos", input_data={
        "name": repo_name,
        "auto_init": True,
        "private": False,
        "description": "Ephemeral repo for Cortex CLI functional tests",
    })

    # Set required custom property (org requires this on all repos)
    gh_api("PATCH", f"/orgs/{org}/properties/values", input_data={
        "repository_names": [repo_name],
        "properties": [
            {"property_name": "cortex-cli-functional-test", "value": "true"}
        ],
    })

    return full_name


def get_default_branch_sha(repo_full_name, retries=5, delay=2):
    """Get the SHA of the HEAD commit on the default branch.

    Retries because GitHub may not have finished initializing the repo
    after auto_init.
    """
    for i in range(retries):
        try:
            result = gh_api("GET", f"/repos/{repo_full_name}/commits/main")
            return result["sha"]
        except RuntimeError:
            if i == retries - 1:
                raise
            time.sleep(delay)


def run_workflow(tag, initial_context, wait=True, timeout=120):
    """Trigger a Cortex workflow via the CLI and return the result."""
    params = [
        "workflows", "run",
        "-t", tag,
        "--context", json.dumps(initial_context),
    ]
    if wait:
        params.extend(["--wait", "--timeout", str(timeout)])

    return cli(params)


def wait_for_workflow_run(tag, run_id, timeout=120):
    """Poll a workflow run until it completes or times out."""
    start = time.time()
    while time.time() - start < timeout:
        result = cli(["workflows", "get-run", "-t", tag, "-r", run_id])
        status = result.get("status", "").upper()
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            return result
        time.sleep(2)

    raise TimeoutError(f"Workflow run {run_id} did not complete within {timeout}s")
