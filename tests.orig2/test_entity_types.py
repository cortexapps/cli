from common import *
# Entity Types were previously known as resource definitions.  That's why the CLI
# command is 'resource-definitions'.  CLI will likely be updated in the future to
# deprecate this.

def test(capsys):
    entity_type = "public-api-type-empty-schema"
    response = cli_command(capsys, ["resource-definitions", "list"])

    if any(entity['type'] == entity_type for entity in response['definitions']):
        cli(["-q", "catalog", "delete-by-type", "-t", entity_type])
        cli(["-q", "resource-definitions", "delete", "-t", entity_type])

    cli_command(capsys, ["resource-definitions", "create", "-f", "data/run-time/create-entity-type-empty-schema.json"])

    response = cli_command(capsys, ["resource-definitions", "list"])
    assert any(entity['type'] == entity_type for entity in response['definitions']), "Entity type should be returned in list"

    response = cli_command(capsys, ["resource-definitions", "get", "-t", entity_type])
    assert response['type'] == entity_type, "Type of returned entity type should be " + entity_type + "."

    cli_command(capsys, ["resource-definitions", "update", "-t", entity_type, "-f", "data/run-time/update-entity-type-empty-schema.json"])

    response = cli_command(capsys, ["resource-definitions", "get", "-t", entity_type])
    assert response['name'] == "Public API Type With Empty Schema -- Update", "Name should be updated for entity type"
    cli(["-q", "catalog", "delete-by-type", "-t", entity_type])
