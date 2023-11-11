"""
Tests for custom-events commands.
"""
from cortexapps_cli.cortex import cli
import json

def _catalog_list(capsys):
    cli(["catalog", "list"])
    out, err = capsys.readouterr()
    json_data = json.loads(out)

    return json_data

def test_custom_events_create(capsys):
    json_data = _catalog_list(capsys)
    if any(entity['tag'] == 'test-custom-event-service' for entity in json_data['entities']):
        cli(["catalog", "delete", "-t", "test-custom-events-service"])
    cli(["catalog", "create", "-f", "tests/test_custom_events_service.yaml"])
    cli(["custom-events", "create", "-t", "test-custom-events-service", "-f", "tests/test_custom_events.json"])

    cli(["custom-events", "create", "-t", "test-custom-events-service", "-f", "tests/test_custom_events_configure.json"])
    out, err = capsys.readouterr()
    out = json.loads(out)
    uuid = out['uuid']

    cli(["custom-events", "get-by-uuid", "-t", "test-custom-events-service", "-u", uuid])
    cli(["custom-events", "update-by-uuid", "-t", "test-custom-events-service", "-u", uuid, "-f", "tests/test_custom_events.json"])
    cli(["custom-events", "delete-by-uuid", "-t", "test-custom-events-service", "-u", uuid])
    cli(["custom-events", "list", "-t", "test-custom-events-service"])
    cli(["custom-events", "list", "-t", "test-custom-events-service", "-y", "VALIDATE_SERVICE"])
    cli(["custom-events", "list", "-t", "test-custom-events-service", "-y", "VALIDATE_SERVICE", "-i", "2023-10-10T13:27:51.226"])
    cli(["custom-events", "delete-all", "-t", "test-custom-events-service"])
