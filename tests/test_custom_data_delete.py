from tests.helpers.utils import *

def test():
    cli(["custom-data", "add", "-t", "recommendations", "-f", "data/run-time/custom-data-delete.json"])

    response = json_response(["custom-data", "get", "-t", "recommendations", "-k", "delete-me"])
    assert response['value'] == "yes"

    cli(["custom-data", "delete", "-t", "recommendations", "-k", "delete-me"])

    response = json_response(["catalog", "details", "-t", "recommendations"])
    assert not any(metadata['key'] == 'delete-me' for metadata in response['metadata'])
