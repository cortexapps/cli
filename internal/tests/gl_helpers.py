import json
import os
import subprocess
import time
import urllib.parse

from helpers.utils import cli, ReturnType

RESOURCE_PREFIX = "cli-functional-test-"
SAFETY_TOPIC = "cortex-cli-functional-test"


def get_env(name):
    """Get a required environment variable or raise."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value


def encode_project(project_path):
    """URL-encode a GitLab project path for API use."""
    return urllib.parse.quote(project_path, safe="")


def gl_api(method, path, input_data=None):
    """Call the GitLab API via the glab CLI.

    Returns parsed JSON response. Raises on non-zero exit code.
    """
    token = get_env("GITLAB_TOKEN")
    cmd = ["glab", "api", "-X", method, path]

    env = {**os.environ, "GITLAB_TOKEN": token}

    if input_data is not None:
        cmd.extend(["-H", "Content-Type: application/json", "--input", "-"])
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
        raise RuntimeError(f"glab api {method} {path} failed: {result.stderr}")

    if not result.stdout.strip():
        return None

    return json.loads(result.stdout)


def safe_delete_project(project_path):
    """Delete a GitLab project, but only if the name matches the safety prefix."""
    project_name = project_path.split("/")[-1]
    if not project_name.startswith(RESOURCE_PREFIX):
        raise RuntimeError(
            f"Refusing to delete project '{project_path}' — "
            f"name does not start with '{RESOURCE_PREFIX}'"
        )
    encoded = encode_project(project_path)
    try:
        gl_api("DELETE", f"projects/{encoded}")
    except RuntimeError:
        pass


def create_test_project(project_name):
    """Create a test project with README and safety topic tag.

    Project is created under the authenticated user's namespace by default.
    """
    project = gl_api("POST", "projects", input_data={
        "name": project_name,
        "path": project_name,
        "initialize_with_readme": True,
        "visibility": "private",
        "topics": [SAFETY_TOPIC],
    })
    return project["path_with_namespace"]


def get_authenticated_user():
    """Get the authenticated GitLab user's username."""
    user = gl_api("GET", "user")
    return user["username"]


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
