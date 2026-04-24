import pytest
from tests.gh_helpers import gh_api, run_workflow, get_env


def _is_org_owner(org, username):
    """Check if the user is an owner of the org."""
    try:
        membership = gh_api("GET", f"/orgs/{org}/memberships/{username}")
        return membership.get("role") == "admin"
    except RuntimeError:
        return False


@pytest.mark.functional
def test_gh_org_member_lifecycle(gh_test_org, import_functional_workflows):
    """Test org member lifecycle: add → remove.

    Exercises github.addUserToOrg and github.removeUserFromOrg workflow
    action blocks in a single flow.

    Note: Skips if GITHUB_TEST_USERNAME is an org owner, since GitHub
    rejects attempts to re-add or demote an admin.
    """
    org = gh_test_org
    username = get_env("GITHUB_TEST_USERNAME")

    if _is_org_owner(org, username):
        pytest.skip(
            f"GITHUB_TEST_USERNAME '{username}' is an org owner — "
            f"cannot test add/remove with the owner account. "
            f"Set GITHUB_TEST_USERNAME to a non-owner GitHub user."
        )

    try:
        # 1. Add user to org via workflow
        result = run_workflow(
            tag="func-test-gh-add-user-to-org",
            initial_context={"org": org, "username": username},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"addUserToOrg workflow failed: {result}"
        )

        # 2. Remove user from org via workflow
        result = run_workflow(
            tag="func-test-gh-remove-user-from-org",
            initial_context={"org": org, "username": username},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"removeUserFromOrg workflow failed: {result}"
        )
    finally:
        # Re-add the user to restore state
        try:
            gh_api("PUT", f"/orgs/{org}/memberships/{username}", input_data={
                "role": "member",
            })
        except RuntimeError:
            pass


@pytest.mark.functional
def test_gh_list_org_members(gh_test_org, import_functional_workflows):
    """Test the github.listOrgMembers workflow action block."""
    result = run_workflow(
        tag="func-test-gh-list-org-members",
        initial_context={"org": gh_test_org},
    )
    assert result.get("status", "").upper() == "COMPLETED", (
        f"listOrgMembers workflow failed: {result}"
    )

    members = gh_api("GET", f"/orgs/{gh_test_org}/members")
    assert members is not None and len(members) > 0, (
        f"Expected at least one member in org '{gh_test_org}', but the list was empty."
    )
