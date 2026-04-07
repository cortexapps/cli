import glob
import os
import tempfile
import uuid

import pytest

from tests.functional.gh_helpers import (
    RESOURCE_PREFIX,
    create_test_repo,
    get_default_branch_sha,
    get_env,
    safe_delete_repo,
    validate_test_org,
)
from tests.helpers.utils import cli, ReturnType


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
    repo_name = f"{RESOURCE_PREFIX}{short_id}"
    full_name = create_test_repo(gh_test_org, repo_name)
    yield full_name
    safe_delete_repo(full_name)


@pytest.fixture(scope="session")
def gh_default_sha(gh_test_repo):
    """Get the SHA of the default branch HEAD commit in the test repo."""
    return get_default_branch_sha(gh_test_repo)


@pytest.fixture(scope="session")
def import_functional_workflows():
    """Import all functional test workflow YAMLs into Cortex.

    Substitutes __GITHUB_INTEGRATION_ALIAS__ placeholder with the
    GITHUB_INTEGRATION_ALIAS env var before importing each workflow.
    """
    alias = get_env("GITHUB_INTEGRATION_ALIAS")
    workflow_dir = "data/functional/workflows"
    yaml_files = sorted(glob.glob(os.path.join(workflow_dir, "*.yaml")))

    assert yaml_files, f"No workflow YAML files found in {workflow_dir}"

    failures = []
    for yaml_path in yaml_files:
        filename = os.path.basename(yaml_path)
        with open(yaml_path, "r") as f:
            content = f.read()

        # Substitute the integration alias placeholder
        content = content.replace("__GITHUB_INTEGRATION_ALIAS__", alias)

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
        except Exception as e:
            failures.append(f"{filename}: {e}")
        finally:
            os.unlink(tmp_path)

    assert not failures, (
        f"Failed to import {len(failures)} workflow(s):\n"
        + "\n".join(failures)
    )
