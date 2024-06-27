"""
Tests for deploys commands.
"""
from cortexapps_cli.cortex import cli
import json

def _add_deploy():
    cli(["deploys", "add", "-t", "cli-test-service", "-f", "tests/test_deploys.json"])

def test_deploys(capsys):
    # This has to be the first call to the cli because we want to capture the output and capsys
    # captures output collectively.
    cli(["deploys", "add", "-t", "cli-test-service", "-f", "tests/test_deploys_uuid.json"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    uuid = out['uuid']

    cli(["-d", "deploys", "update-by-uuid", "-t", "cli-test-service", "-u", uuid, "-f", "tests/test_deploys_update.json"])

    cli(["deploys", "delete-by-uuid", "-t", "cli-test-service", "-u", uuid])

    _add_deploy()

    cli(["deploys", "list", "-t", "cli-test-service"])

    cli(["deploys", "delete", "-t", "cli-test-service", "-s", "SHA-123456"])

    _add_deploy()
    cli(["deploys", "delete-filter", "-y", "DEPLOY"])

    _add_deploy()
    cli(["deploys", "delete-all"])
