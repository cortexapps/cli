"""Sweep job: clean up orphaned functional test resources.

Run with: just test-functional-sweep

This deletes repos and teams left behind by interrupted test runs.
Only deletes resources matching the cli-functional-test- prefix.
"""
import pytest
from tests.functional.gh_helpers import (
    RESOURCE_PREFIX,
    get_env,
    gh_api,
    safe_delete_repo,
    safe_delete_team,
    validate_test_org,
)


def test_sweep():
    """Clean up orphaned test resources from interrupted runs."""
    org = get_env("GITHUB_TEST_ORG")
    validate_test_org(org)

    # Sweep repos
    repos = gh_api("GET", f"/orgs/{org}/repos?per_page=100")
    deleted_repos = []
    for repo in repos:
        if repo["name"].startswith(RESOURCE_PREFIX):
            safe_delete_repo(f"{org}/{repo['name']}")
            deleted_repos.append(repo["name"])

    if deleted_repos:
        print(f"Deleted {len(deleted_repos)} orphaned repo(s): {deleted_repos}")
    else:
        print("No orphaned repos found.")

    # Sweep teams
    teams = gh_api("GET", f"/orgs/{org}/teams?per_page=100")
    deleted_teams = []
    for team in teams:
        if team["slug"].startswith(RESOURCE_PREFIX):
            safe_delete_team(org, team["slug"])
            deleted_teams.append(team["slug"])

    if deleted_teams:
        print(f"Deleted {len(deleted_teams)} orphaned team(s): {deleted_teams}")
    else:
        print("No orphaned teams found.")
