import pytest
from tests.gh_helpers import gh_api, run_workflow, get_env, RESOURCE_PREFIX


@pytest.mark.functional
def test_gh_create_or_update_custom_property_values(gh_test_repo, gh_default_sha, import_functional_workflows):
    """Test the github.createOrUpdateCustomPropertyValues workflow action block.

    Triggers a Cortex workflow that sets a custom property value on the test
    repo, then verifies the property is set via the gh API.

    Note: The 'cortex-cli-functional-test' custom property must already exist
    in the org's custom property schema.
    """
    repo = gh_test_repo

    # 1. Trigger the workflow to create or update custom property values
    result = run_workflow(
        tag="func-test-gh-create-or-update-custom-property-values",
        initial_context={
            "repo": repo,
            "properties": '{"properties":[{"property_name":"cortex-cli-functional-test","value":"true"}]}',
        },
    )

    # 2. Verify the Cortex workflow run completed successfully
    status = result.get("status", "").upper()
    assert status == "COMPLETED", (
        f"Workflow run status was '{status}', expected 'COMPLETED'. "
        f"Full response: {result}"
    )

    # 3. Verify GitHub side-effect: the custom property is set on the repo
    org = repo.split("/")[0]
    repo_name = repo.split("/")[1]
    properties = gh_api("GET", f"/repos/{repo}/properties/values")
    assert properties is not None, (
        f"Expected to find custom properties on repo '{repo}', but got None."
    )
    prop_map = {p["property_name"]: p["value"] for p in properties}
    assert prop_map.get("cortex-cli-functional-test") == "true", (
        f"Expected custom property 'cortex-cli-functional-test' to be 'true' on "
        f"repo '{repo}', but got: {prop_map}"
    )
