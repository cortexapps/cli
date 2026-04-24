import base64

import pytest
from tests.gh_helpers import gh_api, run_workflow


@pytest.mark.functional
def test_gh_pull_request_lifecycle(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test PR lifecycle: create → comment → label.

    Exercises github.createPullRequest, github.createPullRequestComment,
    and github.addLabelToPullRequest workflow action blocks in a single flow.
    """
    branch_name = "cli-functional-test-pr-lifecycle"
    comment_body = "cli-functional-test comment"
    label_name = "cli-functional-test-label"
    repo = gh_test_repo
    org = repo.split("/")[0]

    try:
        gh_api("DELETE", f"/repos/{repo}/git/refs/heads/{branch_name}")
    except RuntimeError:
        pass

    gh_api("POST", f"/repos/{repo}/git/refs", input_data={
        "ref": f"refs/heads/{branch_name}",
        "sha": gh_default_sha,
    })

    pr_number = None
    try:
        gh_api("PUT", f"/repos/{repo}/contents/test-pr-lifecycle-file.txt", input_data={
            "message": "test commit for PR lifecycle",
            "content": base64.b64encode(b"test").decode(),
            "branch": branch_name,
        })

        # 1. Create PR via workflow
        result = run_workflow(
            tag="func-test-gh-create-pull-request",
            initial_context={
                "repo": repo,
                "title": "cli-functional-test-pr-lifecycle",
                "head": branch_name,
                "base": "main",
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createPullRequest workflow failed: {result}"
        )

        # Verify: PR exists
        pulls = gh_api("GET", f"/repos/{repo}/pulls?state=open&head={org}:{branch_name}")
        assert len(pulls) > 0, (
            f"Expected an open PR from branch '{branch_name}', but none found."
        )
        pr_number = pulls[0]["number"]

        # 2. Comment on PR via workflow
        result = run_workflow(
            tag="func-test-gh-create-pull-request-comment",
            initial_context={
                "repo": repo,
                "pull-number": str(pr_number),
                "body": comment_body,
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"createPullRequestComment workflow failed: {result}"
        )

        # Verify: comment exists
        comments = gh_api("GET", f"/repos/{repo}/issues/{pr_number}/comments")
        comment_bodies = [c["body"] for c in comments]
        assert any(comment_body in body for body in comment_bodies), (
            f"Expected comment '{comment_body}' on PR #{pr_number}, got: {comment_bodies}"
        )

        # 3. Add label to PR via workflow
        result = run_workflow(
            tag="func-test-gh-add-label-to-pull-request",
            initial_context={
                "repo": repo,
                "pull-number": str(pr_number),
                "label": label_name,
            },
        )
        assert result.get("status", "").upper() == "COMPLETED", (
            f"addLabelToPullRequest workflow failed: {result}"
        )

        # Verify: label exists on PR
        labels = gh_api("GET", f"/repos/{repo}/issues/{pr_number}/labels")
        label_names = [l["name"] for l in labels]
        assert label_name in label_names, (
            f"Expected label '{label_name}' on PR #{pr_number}, got: {label_names}"
        )
    finally:
        if pr_number is not None:
            try:
                gh_api("PATCH", f"/repos/{repo}/pulls/{pr_number}", input_data={"state": "closed"})
            except RuntimeError:
                pass
        try:
            gh_api("DELETE", f"/repos/{repo}/git/refs/heads/{branch_name}")
        except RuntimeError:
            pass
        try:
            gh_api("DELETE", f"/repos/{repo}/labels/{label_name}")
        except RuntimeError:
            pass
