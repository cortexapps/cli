#!/usr/bin/env python3
"""Delete all functional test workflows from the Cortex instance.

Usage:
    PYTHONPATH=. poetry run python scripts/delete_functional_workflows.py

This script lists all workflows matching the func-test-* tag pattern
and deletes them. Safe to run multiple times.
"""
import glob
import os
import sys

import yaml


def main():
    workflow_dir = "data/functional/workflows"
    yaml_files = sorted(glob.glob(os.path.join(workflow_dir, "*.yaml")))

    if not yaml_files:
        print(f"No workflow YAML files found in {workflow_dir}")
        sys.exit(1)

    tags = []
    for yaml_path in yaml_files:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        tag = data.get("tag")
        if tag:
            tags.append(tag)

    print(f"Found {len(tags)} workflow tags to delete:")
    for tag in tags:
        print(f"  {tag}")

    print()

    from tests.helpers.utils import cli, ReturnType

    deleted = 0
    failed = 0
    for tag in tags:
        try:
            cli(["workflows", "delete", "-t", tag], return_type=ReturnType.RAW)
            print(f"  DELETED: {tag}")
            deleted += 1
        except Exception as e:
            print(f"  SKIP: {tag} ({e})")
            failed += 1

    print(f"\nDone: {deleted} deleted, {failed} skipped/failed")


if __name__ == "__main__":
    main()
