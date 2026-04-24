import pytest
from tests.gh_helpers import gh_api, run_workflow, safe_delete_team, get_env


@pytest.mark.functional
def test_gh_team_lifecycle(gh_test_org, import_functional_workflows):
    """Test team lifecycle: create → get → add user → get membership → list members → remove user → delete.

    Exercises github.createTeam, github.getTeam, github.addUserToTeam,
    github.getTeamMembership, github.listTeamMembers,
    github.removeUserFromTeam, and github.deleteTeam workflow action blocks
    in a single flow.
    """
    org = gh_test_org
    team_name = "cli-functional-test-team-lifecycle"
    team_slug = team_name
    username = get_env("GITHUB_TEST_USERNAME")

    try:
        safe_delete_team(org, team_slug)
    except RuntimeError:
        pass

    try:
        # 1. Create team via workflow
        result = run_workflow(
            tag="func-test-gh-create-team",
            initial_context={"org": org, "team-name": team_name},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createTeam workflow failed: {result}"
        )

        # Verify: team exists
        team = gh_api("GET", f"/orgs/{org}/teams/{team_slug}")
        assert team is not None and team.get("slug") == team_slug, (
            f"Expected team '{team_slug}' to exist, got: {team}"
        )

        # 2. Get team via workflow
        result = run_workflow(
            tag="func-test-gh-get-team",
            initial_context={"org": org, "team": team_slug},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getTeam workflow failed: {result}"
        )

        # 3. Add user to team via workflow
        result = run_workflow(
            tag="func-test-gh-add-user-to-team",
            initial_context={"org": org, "team": team_slug, "username": username},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"addUserToTeam workflow failed: {result}"
        )

        # Verify: user is a member
        members = gh_api("GET", f"/orgs/{org}/teams/{team_slug}/members")
        member_logins = [m["login"] for m in members]
        assert username in member_logins, (
            f"Expected user '{username}' in team '{team_slug}', got: {member_logins}"
        )

        # 4. Get team membership via workflow
        result = run_workflow(
            tag="func-test-gh-get-team-membership",
            initial_context={"org": org, "team": team_slug, "username": username},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"getTeamMembership workflow failed: {result}"
        )

        # 5. List team members via workflow
        result = run_workflow(
            tag="func-test-gh-list-team-members",
            initial_context={"org": org, "team": team_slug},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"listTeamMembers workflow failed: {result}"
        )

        # 6. Remove user from team via workflow
        result = run_workflow(
            tag="func-test-gh-remove-user-from-team",
            initial_context={"org": org, "team": team_slug, "username": username},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"removeUserFromTeam workflow failed: {result}"
        )

        # Verify: user is no longer a member
        members = gh_api("GET", f"/orgs/{org}/teams/{team_slug}/members")
        member_logins = [m["login"] for m in members]
        assert username not in member_logins, (
            f"Expected user '{username}' removed from team '{team_slug}', "
            f"but still in: {member_logins}"
        )

        # 7. Delete team via workflow
        result = run_workflow(
            tag="func-test-gh-delete-team",
            initial_context={"org": org, "team": team_slug},
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"deleteTeam workflow failed: {result}"
        )

        # Verify: team no longer exists
        try:
            gh_api("GET", f"/orgs/{org}/teams/{team_slug}")
            assert False, (
                f"Expected team '{team_slug}' to be deleted, but it still exists."
            )
        except RuntimeError:
            pass  # Expected: team is gone, GET returns 404
    finally:
        try:
            gh_api("DELETE", f"/orgs/{org}/teams/{team_slug}/memberships/{username}")
        except RuntimeError:
            pass
        try:
            safe_delete_team(org, team_slug)
        except RuntimeError:
            pass


@pytest.mark.functional
def test_gh_list_teams(gh_test_org, import_functional_workflows):
    """Test the github.listTeams workflow action block."""
    result = run_workflow(
        tag="func-test-gh-list-teams",
        initial_context={"org": gh_test_org},
    )
    assert result.get("status", "").upper() == "COMPLETED", (
        f"listTeams workflow failed: {result}"
    )
