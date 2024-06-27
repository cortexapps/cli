"""
Tests for custom-events commands.
"""
from cortexapps_cli.cortex import cli
import json
import time

def test_custom_events_create(capsys):
    cli(["custom-events", "create", "-t", "test-service", "-f", "tests/custom-events.json"])
    cli(["custom-events", "list", "-t", "test-service"])
    cli(["custom-events", "list", "-t", "test-service", "-y", "VALIDATE_SERVICE"])
    cli(["custom-events", "list", "-t", "test-service", "-y", "VALIDATE_SERVICE", "-i", "2023-10-10T13:27:51.226"])


def test_custom_event_uuid(capsys):
    cli(["custom-events", "create", "-t", "test-service", "-f", "tests/custom-events-configure.json"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    uuid = out['uuid']
    cli(["custom-events", "get-by-uuid", "-t", "test-service", "-u", uuid])
    cli(["custom-events", "update-by-uuid", "-t", "test-service", "-u", uuid, "-f", "tests/custom-events.json"])
    cli(["custom-events", "delete-by-uuid", "-t", "test-service", "-u", uuid])
    cli(["custom-events", "delete-all", "-t", "test-service"])

