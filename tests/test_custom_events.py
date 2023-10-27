"""
Tests for custom-events commands.
"""
from cortexapps_cli.cortex import cli
import json

def test_custom_events_create():
    cli(["custom-events", "create", "-t", "test-service", "-f", "tests/custom-events.json"])

def test_custom_events_uuid(capsys):
    cli(["custom-events", "create", "-t", "test-service", "-f", "tests/custom-events-configure.json"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    uuid = out['uuid']
    cli(["custom-events", "get-by-uuid", "-t", "test-service", "-u", uuid])
    out, err = capsys.readouterr()
    out = json.loads(out)
    uuid1 = out['uuid']
    assert uuid == uuid1, "UUID requested should match UUID of returned event"
    cli(["custom-events", "update-by-uuid", "-t", "test-service", "-u", uuid, "-f", "tests/custom-events.json"])
    cli(["custom-events", "delete-by-uuid", "-t", "test-service", "-u", uuid])

def test_custom_events_list():
    cli(["custom-events", "list", "-t", "test-service"])

def test_custom_events_list():
    cli(["custom-events", "list", "-t", "test-service", "-y", "VALIDATE_SERVICE"])

def test_custom_events_list():
    cli(["custom-events", "list", "-t", "test-service", "-y", "VALIDATE_SERVICE", "-i", "2023-10-10T13:27:51.226"])

def test_custom_events_delete(capsys):
    cli(["custom-events", "delete-all", "-t", "test-service"])
    cli(["custom-events", "list", "-t", "test-service"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    assert len(out['events']) == 0, "All custom events should have been deleted"
