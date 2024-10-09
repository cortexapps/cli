from tests.helpers.utils import *

def test():
    cli(["custom-data", "add", "-t", "recommendations", "-f", "data/run-time/custom-data-delete.json"])

    result = cli(["custom-data", "get", "-t", "recommendations", "-k", "delete-me"])
    assert result['value'] == "yes"

    cli(["custom-data", "delete", "-t", "recommendations", "-k", "delete-me"])

    result = cli(["catalog", "details", "-t", "recommendations"])
    assert not any(metadata['key'] == 'delete-me' for metadata in result['metadata'])
