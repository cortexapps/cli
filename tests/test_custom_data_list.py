from common import *

def test(capsys):
    response = cli_command(capsys, ["catalog", "details", "-t", "backend-worker"])
    list = [metadata for metadata in response['metadata'] if metadata['key'] == "cicd"]
    assert list[0]['value'] == "circle-ci"
