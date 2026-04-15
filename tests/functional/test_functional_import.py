import glob
import os
import tempfile

import pytest
from tests.helpers.utils import cli, ReturnType


@pytest.mark.setup
def test():
    """Import functional test data (workflow YAMLs) into Cortex.

    Substitutes integration alias placeholders before importing.
    Skips files whose required alias env var is not set.
    """
    gh_alias = os.environ.get("GITHUB_INTEGRATION_ALIAS", "")
    gl_alias = os.environ.get("GITLAB_INTEGRATION_ALIAS", "")

    assert gh_alias or gl_alias, (
        "At least one of GITHUB_INTEGRATION_ALIAS or GITLAB_INTEGRATION_ALIAS "
        "must be set"
    )

    workflow_dir = "data/functional/workflows"
    yaml_files = sorted(glob.glob(os.path.join(workflow_dir, "*.yaml")))
    assert yaml_files, f"No workflow YAML files found in {workflow_dir}"

    failures = []
    imported = 0
    skipped = 0
    for yaml_path in yaml_files:
        filename = os.path.basename(yaml_path)

        if filename.startswith("gh-") and not gh_alias:
            skipped += 1
            print(f"SKIP: {filename} (GITHUB_INTEGRATION_ALIAS not set)")
            continue
        if filename.startswith("gl-") and not gl_alias:
            skipped += 1
            print(f"SKIP: {filename} (GITLAB_INTEGRATION_ALIAS not set)")
            continue

        with open(yaml_path, "r") as f:
            content = f.read()

        if gh_alias:
            content = content.replace("__GITHUB_INTEGRATION_ALIAS__", gh_alias)
        if gl_alias:
            content = content.replace("__GITLAB_INTEGRATION_ALIAS__", gl_alias)

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
                print(f"FAILED: {filename}")
                print(result.stdout)
            else:
                imported += 1
                print(f"OK: {filename}")
        except Exception as e:
            failures.append(f"{filename}: {e}")
        finally:
            os.unlink(tmp_path)

    print(f"\nImported: {imported}, Skipped: {skipped}, Failed: {len(failures)}")

    assert not failures, (
        f"Failed to import {len(failures)} workflow(s):\n"
        + "\n".join(failures)
    )
