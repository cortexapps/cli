import os
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
    """Import all functional test workflow YAMLs into Cortex."""
    result = cli(
        ["backup", "import", "-d", "data/functional"],
        return_type=ReturnType.STDOUT,
    )
    return result
