import glob
import os
import tempfile
import uuid

import pytest

from tests.functional.gh_helpers import (
    RESOURCE_PREFIX as GH_RESOURCE_PREFIX,
    create_test_repo,
    get_default_branch_sha,
    get_env,
    safe_delete_repo,
    validate_test_org,
)
from tests.functional.gl_helpers import (
    RESOURCE_PREFIX as GL_RESOURCE_PREFIX,
    create_test_project,
    encode_project,
    get_authenticated_user,
    gl_api,
    safe_delete_project,
)
from tests.helpers.utils import cli, ReturnType


# ---------------------------------------------------------------------------
# GitHub fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def gh_test_org():
    """Validate the test org exists and has the safety marker."""
    org = get_env("GITHUB_TEST_ORG")
    validate_test_org(org)
    return org


@pytest.fixture(scope="session")
def gh_test_repo(gh_test_org):
    """Create an ephemeral test repo, yield its full name, then delete it."""
    short_id = uuid.uuid4().hex[:8]
    repo_name = f"{GH_RESOURCE_PREFIX}{short_id}"
    full_name = create_test_repo(gh_test_org, repo_name)
    yield full_name
    safe_delete_repo(full_name)


@pytest.fixture(scope="session")
def gh_default_sha(gh_test_repo):
    """Get the SHA of the default branch HEAD commit in the test repo."""
    return get_default_branch_sha(gh_test_repo)


# ---------------------------------------------------------------------------
# GitLab fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def gl_test_namespace():
    """Get the authenticated GitLab user's username."""
    return get_authenticated_user()


@pytest.fixture(scope="session")
def gl_test_project(import_functional_workflows):
    """Create an ephemeral GitLab test project, yield its path, then delete."""
    short_id = uuid.uuid4().hex[:8]
    project_name = f"{GL_RESOURCE_PREFIX}{short_id}"
    project_path = create_test_project(project_name)
    yield project_path
    safe_delete_project(project_path)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def import_functional_workflows():
    """Import all functional test workflow YAMLs into Cortex.

    Substitutes integration alias placeholders before importing each workflow.
    Skips files whose required alias env var is not set.
    """
    gh_alias = os.environ.get("GITHUB_INTEGRATION_ALIAS", "")
    gl_alias = os.environ.get("GITLAB_INTEGRATION_ALIAS", "")

    workflow_dir = "data/functional/workflows"
    yaml_files = sorted(glob.glob(os.path.join(workflow_dir, "*.yaml")))

    assert yaml_files, f"No workflow YAML files found in {workflow_dir}"

    failures = []
    imported = 0
    skipped = 0
    for yaml_path in yaml_files:
        filename = os.path.basename(yaml_path)

        # Skip files that need an alias we don't have
        if filename.startswith("gh-") and not gh_alias:
            skipped += 1
            continue
        if filename.startswith("gl-") and not gl_alias:
            skipped += 1
            continue

        with open(yaml_path, "r") as f:
            content = f.read()

        # Substitute integration alias placeholders
        if gh_alias:
            content = content.replace("__GITHUB_INTEGRATION_ALIAS__", gh_alias)
        if gl_alias:
            content = content.replace("__GITLAB_INTEGRATION_ALIAS__", gl_alias)

        # Write to a temp file and import via CLI
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = cli(
                ["workflows", "create", "-f", tmp_path],
                return_type=ReturnType.RAW,
            )
            if result.exit_code != 0:
                failures.append(f"{filename}: exit code {result.exit_code}\n{result.stdout}")
            else:
                imported += 1
        except Exception as e:
            failures.append(f"{filename}: {e}")
        finally:
            os.unlink(tmp_path)

    assert not failures, (
        f"Failed to import {len(failures)} workflow(s):\n"
        + "\n".join(failures)
    )
