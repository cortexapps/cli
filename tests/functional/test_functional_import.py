import glob
import os
import tempfile

import pytest
from tests.helpers.utils import cli, ReturnType


@pytest.mark.setup
def test():
    """Import functional test data (workflow YAMLs) into Cortex.

    Substitutes __GITHUB_INTEGRATION_ALIAS__ with the env var before importing.
    """
    alias = os.environ.get("GITHUB_INTEGRATION_ALIAS")
    assert alias, "GITHUB_INTEGRATION_ALIAS env var is not set"

    workflow_dir = "data/functional/workflows"
    yaml_files = sorted(glob.glob(os.path.join(workflow_dir, "*.yaml")))
    assert yaml_files, f"No workflow YAML files found in {workflow_dir}"

    failures = []
    for yaml_path in yaml_files:
        filename = os.path.basename(yaml_path)
        with open(yaml_path, "r") as f:
            content = f.read()

        content = content.replace("__GITHUB_INTEGRATION_ALIAS__", alias)

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
                print(f"OK: {filename}")
        except Exception as e:
            failures.append(f"{filename}: {e}")
        finally:
            os.unlink(tmp_path)

    assert not failures, (
        f"Failed to import {len(failures)} workflow(s):\n"
        + "\n".join(failures)
    )
